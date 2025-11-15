def get_material_budget(plan, cent=5):
    """
    Calculate material budget for a given plan.
    Quantities scale directly with plot size in cents.
    """
    # Base multiplier for plan type
    plan_multiplier = {
        "2BHK": 1.0,
        "3BHK": 1.5,
        "Duplex": 2.0
    }.get(plan, 1.0)

    # Grouped materials with base quantities
    grouped_materials = {
        "Foundation": [
            {"item": "Cement (bags)", "base_qty": 300, "rate": 400},
            {"item": "M-Sand (tons)", "base_qty": 15, "rate": 2500},
            {"item": "Crushed Stone (tons)", "base_qty": 12, "rate": 2200},
            {"item": "Steel (TMT Bars, tons)", "base_qty": 2, "rate": 60000},
            {"item": "Anti-Termite Chemical (litres)", "base_qty": 20, "rate": 250},
        ],
        "Superstructure": [
            {"item": "Bricks (units)", "base_qty": 8000, "rate": 9},
            {"item": "Binding Wire (kg)", "base_qty": 50, "rate": 90},
            {"item": "Formwork (sheets)", "base_qty": 15, "rate": 1200},
        ],
        "Roofing": [
            {"item": "Roof Waterproofing Membrane (sq.ft)", "base_qty": 800, "rate": 40},
            {"item": "Concrete Mix (cu.m)", "base_qty": 20, "rate": 6000},
        ],
        "Doors & Windows": [
            {"item": "Main Door", "base_qty": 1, "rate": 12000},
            {"item": "Window (UPVC)", "base_qty": 6, "rate": 4500},
        ],
        "Flooring & Finishing": [
            {"item": "Vitrified Tiles (sq.ft)", "base_qty": 1000, "rate": 60},
            {"item": "Wall Putty (kg)", "base_qty": 100, "rate": 750},
            {"item": "Paint (litres)", "base_qty": 50, "rate": 300},
        ],
        "Kitchen": [
            {"item": "Granite Countertop (sq.ft)", "base_qty": 30, "rate": 250},
            {"item": "Sink (SS)", "base_qty": 1, "rate": 3500},
        ],
        "Bathroom": [
            {"item": "Toilet Set", "base_qty": 2, "rate": 5000},
            {"item": "Shower Mixer", "base_qty": 2, "rate": 2000},
            {"item": "Tiles (Bathroom, sq.ft)", "base_qty": 300, "rate": 60},
        ],
        "Plumbing": [
            {"item": "PVC Pipes (ft)", "base_qty": 500, "rate": 40},
            {"item": "Valves & Fittings", "base_qty": 20, "rate": 150},
        ],
        "Electrical": [
            {"item": "Wiring (meters)", "base_qty": 1000, "rate": 20},
            {"item": "Switches and Boards", "base_qty": 20, "rate": 200},
            {"item": "Fans & Lights", "base_qty": 10, "rate": 1500},
        ],
        "Staircase": [
            {"item": "Staircase Concrete", "base_qty": 10, "rate": 5000},
            {"item": "Railings (ft)", "base_qty": 25, "rate": 300},
        ] if plan == "Duplex" else [],
        "External Works": [
            {"item": "Compound Wall (ft)", "base_qty": 100, "rate": 600},
            {"item": "Main Gate", "base_qty": 1, "rate": 15000},
        ]
    }

    final_data = {}
    grand_total = 0

    for section, items in grouped_materials.items():
        final_data[section] = []
        for m in items:
            # Scale quantity directly with plan_multiplier and cent
            qty = round(m["base_qty"] * plan_multiplier * cent, 2)
            total = round(qty * m["rate"], 2)
            grand_total += total
            final_data[section].append({
                "item": m["item"],
                "quantity": qty,
                "rate": m["rate"],
                "total": total
            })

    return final_data, grand_total
