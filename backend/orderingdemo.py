import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(find_dotenv())

BUSYNESS_COEFF = 1.34  # fixed for demo purposes

TSX_PATH = Path("components") / "dashboard" / "inventory-overview-demo.tsx"

# Your backend-ish inventory data (SKU-based)
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
# (Adjust names if your UI changes)
UI_ITEM_MAP = {
    "Cups": {"sku": "paper_cups_12oz", "unit": ""},         # UI shows plain numbers
    "Coffee Beans": {"sku": "decaf_beans", "unit": "kg"},   # pick decaf as the one low in your data
    "Milk": {"sku": "oat_milk", "unit": "L"},               # your inventory uses liters
    "Donuts": {"sku": "croissants", "unit": ""},            # demo mapping
    "Napkins": {"sku": "napkins", "unit": ""},              # packs, but UI shows number -> fine
}

# For each UI row, a simple "estimated requirement" baseline (demo)
# You can later compute this based on predicted traffic.
UI_ESTIMATED_REQUIREMENT = {
    "Cups": 450,
    "Coffee Beans": 120,  # kg
    "Milk": 80,           # L
    "Donuts": 90,
    "Napkins": 200,
}


def snapshot_low_stock(inventory: dict) -> list[dict]:
    """Low-stock rule: stock < reorder_level."""
    low = []
    for sku, item in inventory.items():
        if item["stock"] < item["reorder_level"]:
            gap = item["reorder_level"] - item["stock"]
            suggested_qty = math.ceil(gap * BUSYNESS_COEFF)

            low.append({
                "sku": sku,
                "category": item["category"],
                "unit": item["unit"],
                "stock": item["stock"],
                "reorder_level": item["reorder_level"],
                "suggested_order_qty": suggested_qty,
                "unit_cost": item["price"],
                "est_line_cost": round(suggested_qty * item["price"], 2),
            })
    return low


def build_prompt(low_snapshot: list[dict]) -> str:
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
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("Could not find JSON object in model output.")
    return json.loads(m.group(0))


def apply_orders_to_inventory(inventory: dict, purchase_payload: dict) -> dict:
    updated = json.loads(json.dumps(inventory))  # deep copy

    for line in purchase_payload.get("purchase_lines", []):
        sku = line["sku"]
        qty = float(line["suggested_order_qty"])
        if sku in updated:
            updated[sku]["stock"] = round(float(updated[sku]["stock"]) + qty, 3)

    return updated


def format_value(value: float, unit: str) -> str:
    # For nice demo output (avoid 18.0 -> 18)
    if abs(value - round(value)) < 1e-9:
        value_str = str(int(round(value)))
    else:
        value_str = str(value)

    return f"{value_str} {unit}".strip()


def build_updated_rows_tsx(updated_inventory: dict, low_snapshot: list[dict]) -> str:
    """
    Build a TSX array literal for `initialRows` matching your InventoryRow type.
    """
    low_skus = {x["sku"] for x in low_snapshot}

    rows = []
    i = 1
    for item_label, meta in UI_ITEM_MAP.items():
        sku = meta["sku"]
        ui_unit = meta["unit"]
        inv = updated_inventory.get(sku)

        # If SKU isn't found, keep something sane
        stock = float(inv["stock"]) if inv else 0.0

        est_req = UI_ESTIMATED_REQUIREMENT.get(item_label, 0)

        estimatedRequirement = (
            format_value(est_req, ui_unit) if ui_unit else format_value(est_req, "")
        )
        stockRemaining = (
            format_value(stock, ui_unit) if ui_unit else format_value(stock, "")
        )

        # Status logic:
        # - If it was low stock => we placed an order => "shipment"
        # - If still 0 after update => outOfStock
        # - Else => noAction
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

    m = pattern.search(tsx_text)
    if not m:
        raise ValueError("Could not locate `const initialRows: InventoryRow[] = [...]` block in TSX file.")

    return pattern.sub(rf"\1{new_array_literal}\n", tsx_text, count=1)


def main():
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        raise EnvironmentError("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment.")

    low_snapshot = snapshot_low_stock(cafe_inventory)

    # If nothing low-stock, still update the TSX to reflect current inventory
    prompt = build_prompt(low_snapshot)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
    )

    purchase_payload = {"purchase_lines": [], "system_events": [], "timestamp_utc": ""}
    if low_snapshot:
        resp = llm.invoke(prompt)
        purchase_payload = extract_json_strict(resp.content)

    updated_inventory = apply_orders_to_inventory(cafe_inventory, purchase_payload)

    if not TSX_PATH.exists():
        raise FileNotFoundError(f"TSX file not found at: {TSX_PATH.resolve()}")

    tsx_text = TSX_PATH.read_text(encoding="utf-8")
    new_rows_literal = build_updated_rows_tsx(updated_inventory, low_snapshot)
    updated_tsx = replace_initial_rows_block(tsx_text, new_rows_literal)
    TSX_PATH.write_text(updated_tsx, encoding="utf-8")

    print("✅ Updated:", TSX_PATH.as_posix())
    if low_snapshot:
        print("✅ Orders placed for low-stock SKUs:", ", ".join(sorted({x["sku"] for x in low_snapshot})))
        if purchase_payload.get("system_events"):
            print("Sample event:", purchase_payload["system_events"][0])


if __name__ == "__main__":
    main()
