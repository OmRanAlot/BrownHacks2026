import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(find_dotenv())

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
BUSYNESS_COEFF = 1.34  # fixed for demo purposes
TSX_PATH = Path("components") / "dashboard" / "inventory-overview-demo.tsx"

# Email-ready export file (JSON) - no exports folder
EMAIL_EXPORT_PATH = Path("inventory_status_email.json")

# ---------------------------------------------------------------------
# Inventory (backend-ish SKU store)
# ---------------------------------------------------------------------
cafe_inventory = {
    "espresso_beans": {"category": "coffee", "unit": "kg", "stock": 18.5, "reorder_level": 5, "price": 28.00},
    "decaf_beans": {"category": "coffee", "unit": "kg", "stock": 3.2, "reorder_level": 4, "price": 30.50},
    "oat_milk": {"category": "milk", "unit": "liters", "stock": 6, "reorder_level": 10, "price": 3.80},
    "whole_milk": {"category": "milk", "unit": "liters", "stock": 22, "reorder_level": 8, "price": 2.40},
    "almond_milk": {"category": "milk", "unit": "liters", "stock": 2, "reorder_level": 6, "price": 4.20},
    "croissants": {"category": "pastry", "unit": "pieces", "stock": 14, "reorder_level": 20, "price": 1.75},
    "blueberry_muffins": {"category": "pastry", "unit": "pieces", "stock": 4, "reorder_level": 12, "price": 2.10},
    "paper_cups_12oz": {"category": "supplies", "unit": "cups", "stock": 420, "reorder_level": 300, "price": 0.08},
    "napkins": {"category": "supplies", "unit": "packs", "stock": 1, "reorder_level": 5, "price": 2.50},
    "syrup_caramel": {"category": "syrup", "unit": "ml", "stock": 450, "reorder_level": 800, "price": 0.014},
}

# Map your TSX "Item" labels -> backend SKUs + how to format units
UI_ITEM_MAP = {
    "Cups": {"sku": "paper_cups_12oz", "unit": ""},         # UI shows plain numbers
    "Coffee Beans": {"sku": "decaf_beans", "unit": "kg"},   # pick decaf as the one low in your data
    "Milk": {"sku": "oat_milk", "unit": "L"},               # UI uses L; inventory stores liters
    "Donuts": {"sku": "croissants", "unit": ""},            # demo mapping
    "Napkins": {"sku": "napkins", "unit": ""},              # packs, but UI shows number -> fine
}

# For each UI row, a simple "estimated requirement" baseline (demo)
UI_ESTIMATED_REQUIREMENT = {
    "Cups": 450,
    "Coffee Beans": 120,  # kg
    "Milk": 80,           # L
    "Donuts": 90,
    "Napkins": 200,
}


# ---------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------
def money(x: float) -> str:
    return f"${x:,.2f}"


def pct(x: float) -> str:
    return f"{x:.1f}%"


def format_value(value: float, unit: str) -> str:
    """Format numeric values cleanly for UI strings."""
    if abs(value - round(value)) < 1e-9:
        value_str = str(int(round(value)))
    else:
        value_str = str(value)
    return f"{value_str} {unit}".strip()


# ---------------------------------------------------------------------
# Inventory logic
# ---------------------------------------------------------------------
def snapshot_low_stock(inventory: dict) -> list[dict]:
    """Low-stock rule: stock < reorder_level."""
    low = []
    for sku, item in inventory.items():
        if float(item["stock"]) < float(item["reorder_level"]):
            gap = float(item["reorder_level"]) - float(item["stock"])
            suggested_qty = math.ceil(gap * BUSYNESS_COEFF)

            low.append({
                "sku": sku,
                "category": item["category"],
                "unit": item["unit"],
                "stock": float(item["stock"]),
                "reorder_level": float(item["reorder_level"]),
                "suggested_order_qty": suggested_qty,
                "unit_cost": float(item["price"]),
                "est_line_cost": round(suggested_qty * float(item["price"]), 2),
            })
    return low


def build_prompt(low_snapshot: list[dict]) -> str:
    """Build a strict JSON-only prompt for Gemini."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    schema = {
        "timestamp_utc": "string",
        "purchase_lines": [
            {
                "sku": "string",
                "suggested_order_qty": "number"
            }
        ],
        "system_events": ["string"]
    }

    return f"""
Return ONLY valid JSON (no markdown, no backticks, no extra text) matching this schema exactly:
{json.dumps(schema, indent=2)}

Rules:
- Use suggested_order_qty EXACTLY as provided in the snapshot (do not change).
- sku must match a snapshot sku exactly.
- timestamp_utc must be "{now}".
- Provide 4 to 8 short system_events that read like system logs.

Low-stock snapshot JSON:
{json.dumps(low_snapshot, indent=2)}
""".strip()


def extract_json_strict(text: str) -> dict:
    """Extract JSON, strictly preferring full-body JSON; fallback to first {...} match."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("Could not find JSON object in model output.")
    return json.loads(m.group(0))


def validate_purchase_payload(payload: dict, low_snapshot: list[dict]) -> dict:
    """
    Ensure payload structure is sane and that SKUs + quantities match the snapshot rules.
    If invalid, raise ValueError.
    """
    if not isinstance(payload, dict):
        raise ValueError("Purchase payload must be a JSON object.")

    for key in ("timestamp_utc", "purchase_lines", "system_events"):
        if key not in payload:
            raise ValueError(f"Purchase payload missing key: {key}")

    if not isinstance(payload["purchase_lines"], list):
        raise ValueError("purchase_lines must be a list.")
    if not isinstance(payload["system_events"], list):
        raise ValueError("system_events must be a list.")

    snapshot_map = {x["sku"]: x["suggested_order_qty"] for x in low_snapshot}

    for line in payload["purchase_lines"]:
        if not isinstance(line, dict):
            raise ValueError("Each purchase line must be an object.")
        if "sku" not in line or "suggested_order_qty" not in line:
            raise ValueError("Each purchase line must contain sku and suggested_order_qty.")

        sku = line["sku"]
        qty = line["suggested_order_qty"]

        if sku not in snapshot_map:
            raise ValueError(f"Payload contains unknown sku not in snapshot: {sku}")

        expected_qty = snapshot_map[sku]
        if float(qty) != float(expected_qty):
            raise ValueError(f"Qty mismatch for {sku}: expected {expected_qty}, got {qty}")

    return payload


def apply_orders_to_inventory(inventory: dict, purchase_payload: dict) -> dict:
    """Apply purchase order quantities to inventory stock."""
    updated = json.loads(json.dumps(inventory))  # deep copy

    for line in purchase_payload.get("purchase_lines", []) or []:
        sku = line["sku"]
        qty = float(line["suggested_order_qty"])
        if sku in updated:
            updated[sku]["stock"] = round(float(updated[sku]["stock"]) + qty, 3)

    return updated


# ---------------------------------------------------------------------
# Reporting (industry-style output)
# ---------------------------------------------------------------------
def build_inventory_report(inventory_before: dict, inventory_after: dict, low_snapshot: list[dict], purchase_payload: dict) -> str:
    """Generate a professional inventory report suitable for console logs / email body."""

    def inv_value(inv: dict) -> float:
        return sum(float(it["stock"]) * float(it["price"]) for it in inv.values())

    def count_low(inv: dict) -> int:
        return sum(1 for it in inv.values() if float(it["stock"]) < float(it["reorder_level"]))

    def count_out(inv: dict) -> int:
        return sum(1 for it in inv.values() if float(it["stock"]) <= 0)

    total_skus = len(inventory_after)
    low_count = count_low(inventory_after)
    out_count = count_out(inventory_after)

    before_value = inv_value(inventory_before)
    after_value = inv_value(inventory_after)

    system_ts = purchase_payload.get("timestamp_utc") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Health rating
    health = "GREEN"
    if out_count > 0:
        health = "RED"
    elif low_count > 0:
        health = "AMBER"

    total_order_cost = sum(float(x.get("est_line_cost", 0.0)) for x in low_snapshot)

    # Category breakdown
    by_category = {}
    for _, item in inventory_after.items():
        cat = item["category"]
        by_category.setdefault(cat, {"skus": 0, "value": 0.0, "low": 0, "out": 0})
        by_category[cat]["skus"] += 1
        by_category[cat]["value"] += float(item["stock"]) * float(item["price"])
        if float(item["stock"]) < float(item["reorder_level"]):
            by_category[cat]["low"] += 1
        if float(item["stock"]) <= 0:
            by_category[cat]["out"] += 1

    lines = []
    lines.append("=" * 76)
    lines.append(f"INVENTORY STATUS REPORT  |  {system_ts}")
    lines.append("=" * 76)

    lines.append("EXECUTIVE SUMMARY")
    lines.append(f"- Inventory Health: {health}")
    lines.append(f"- SKUs Tracked: {total_skus}")
    lines.append(f"- Low-stock: {low_count} ({pct(100.0 * low_count / max(total_skus, 1))})")
    lines.append(f"- Out-of-stock: {out_count}")
    if low_snapshot:
        lines.append(f"- Replenishment Suggested: {len(low_snapshot)} line(s) | Est. Order Cost: {money(total_order_cost)}")
    else:
        lines.append("- Replenishment Suggested: none")
    lines.append("")

    lines.append("VALUATION (AT COST)")
    lines.append(f"- Before: {money(before_value)}")
    lines.append(f"- After : {money(after_value)}")
    if low_snapshot:
        lines.append(f"- Delta : {money(after_value - before_value)} (post-replenishment)")
    lines.append("")

    lines.append("CATEGORY BREAKDOWN (AFTER)")
    for cat in sorted(by_category.keys()):
        d = by_category[cat]
        lines.append(
            f"- {cat.title():<12} | SKUs: {d['skus']:<2} | Value: {money(d['value']):>12} | Low: {d['low']:<2} | OOS: {d['out']:<2}"
        )
    lines.append("")

    if low_snapshot:
        lines.append("REPLENISHMENT RECOMMENDATIONS")
        lines.append("SKU                  CATEGORY      ON HAND        REORDER @      SUGGESTED      EST. COST")
        lines.append("-" * 76)

        for x in sorted(low_snapshot, key=lambda z: float(z["est_line_cost"]), reverse=True):
            sku = x["sku"]
            cat = x["category"]
            unit = inventory_before[sku]["unit"]
            on_hand = format_value(float(inventory_before[sku]["stock"]), unit)
            reorder = format_value(float(x["reorder_level"]), unit)
            sug = format_value(float(x["suggested_order_qty"]), unit)
            cost = money(float(x["est_line_cost"]))
            lines.append(f"{sku:<20} {cat:<12} {on_hand:<12} {reorder:<12} {sug:<12} {cost:>10}")

        lines.append("")

    system_events = purchase_payload.get("system_events") or []
    if system_events:
        lines.append("SYSTEM EVENTS (SAMPLE)")
        for e in system_events[:6]:
            lines.append(f"- {e}")
        if len(system_events) > 6:
            lines.append(f"- (+{len(system_events) - 6} more)")
        lines.append("")

    lines.append("=" * 76)
    return "\n".join(lines)


# ---------------------------------------------------------------------
# Email export feature (JSON)
# ---------------------------------------------------------------------
def build_email_payload(report_text: str, purchase_payload: dict) -> dict:
    """
    Create a JSON object suitable to send via an email service.
    (You can later POST this to SendGrid, SES, Gmail API, etc.)
    """
    ts = purchase_payload.get("timestamp_utc") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"Inventory Status Report — {ts}"

    body_lines = [
        "Hi team,",
        "",
        "Please find the latest inventory status report below:",
        "",
        report_text,
        "",
        "Regards,",
        "Inventory System",
    ]

    return {
        "subject": subject,
        "body_text": "\n".join(body_lines),
        "generated_at_utc": ts,
        "tags": ["inventory", "status_report"],
    }


def export_email_payload_json(payload: dict, out_path: Path = EMAIL_EXPORT_PATH) -> Path:
    """Write the email payload to a JSON file in the current directory (no folders created)."""
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------
# TSX update logic
# ---------------------------------------------------------------------
def build_updated_rows_tsx(updated_inventory: dict, low_snapshot: list[dict]) -> str:
    """Build a TSX array literal for `initialRows` matching your InventoryRow type."""
    low_skus = {x["sku"] for x in low_snapshot}

    rows = []
    i = 1
    for item_label, meta in UI_ITEM_MAP.items():
        sku = meta["sku"]
        ui_unit = meta["unit"]
        inv = updated_inventory.get(sku)

        stock = float(inv["stock"]) if inv else 0.0
        est_req = UI_ESTIMATED_REQUIREMENT.get(item_label, 0)

        estimatedRequirement = format_value(est_req, ui_unit) if ui_unit else format_value(est_req, "")
        stockRemaining = format_value(stock, ui_unit) if ui_unit else format_value(stock, "")

        if sku in low_skus:
            status = "shipment"
        elif stock <= 0:
            status = "outOfStock"
        else:
            status = "noAction"

        rows.append(
            f'  {{ id: "{i}", item: "{item_label}", estimatedRequirement: "{estimatedRequirement}", '
            f'stockRemaining: "{stockRemaining}", status: "{status}" }},'
        )
        i += 1

    return "[\n" + "\n".join(rows) + "\n]"


def replace_initial_rows_block(tsx_text: str, new_array_literal: str) -> str:
    """
    Replace:
    const initialRows: InventoryRow[] = [
      ...
    ]
    with the new literal.
    """
    pattern = re.compile(
        r"(const\s+initialRows\s*:\s*InventoryRow\[\]\s*=\s*)\[\s*\n.*?\n\]\s*",
        flags=re.DOTALL
    )

    if not pattern.search(tsx_text):
        raise ValueError("Could not locate `const initialRows: InventoryRow[] = [...]` block in TSX file.")

    return pattern.sub(rf"\1{new_array_literal}\n", tsx_text, count=1)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    api_key_present = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if not api_key_present:
        raise EnvironmentError("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment.")

    inventory_before = json.loads(json.dumps(cafe_inventory))  # deep copy (for reporting)
    low_snapshot = snapshot_low_stock(cafe_inventory)

    purchase_payload = {"purchase_lines": [], "system_events": [], "timestamp_utc": ""}

    if low_snapshot:
        prompt = build_prompt(low_snapshot)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
        )
        resp = llm.invoke(prompt)
        purchase_payload = extract_json_strict(resp.content)
        purchase_payload = validate_purchase_payload(purchase_payload, low_snapshot)

    updated_inventory = apply_orders_to_inventory(cafe_inventory, purchase_payload)

    # --- Professional Inventory Summary Output ---
    report_text = build_inventory_report(inventory_before, updated_inventory, low_snapshot, purchase_payload)
    print(report_text)

    # --- Export email-ready JSON payload (no folders created) ---
    email_payload = build_email_payload(report_text, purchase_payload)
    export_path = export_email_payload_json(email_payload, EMAIL_EXPORT_PATH)
    print(f"📩 Email JSON payload written to: {export_path.as_posix()}")

    # --- Update TSX ---
    if not TSX_PATH.exists():
        raise FileNotFoundError(f"TSX file not found at: {TSX_PATH.resolve()}")

    tsx_text = TSX_PATH.read_text(encoding="utf-8")
    new_rows_literal = build_updated_rows_tsx(updated_inventory, low_snapshot)
    updated_tsx = replace_initial_rows_block(tsx_text, new_rows_literal)
    TSX_PATH.write_text(updated_tsx, encoding="utf-8")

    print(f"✅ TSX updated: {TSX_PATH.as_posix()}")


if __name__ == "__main__":
    main()
