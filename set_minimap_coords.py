"""
Odoo Shell Script - Auto-assign minimap coordinates to all internal locations
Run with:
    python odoo-src/odoo-bin shell -c odoo.conf -d YOUR_DB --no-http < set_minimap_coords.py

Algorithm:
  - Leaf nodes get sequential X positions (no two leaves share X)
  - Parent X = midpoint of its children's X range
  - Y = depth in hierarchy
  - Result: clean tree layout with no overlapping cells
"""

from collections import defaultdict

all_locations = env['stock.location'].search(
    [('usage', '=', 'internal')],
    order='complete_name'
)

if not all_locations:
    print("No internal locations found.")
    raise SystemExit

print(f"Found {len(all_locations)} internal location(s).\n")

internal_ids = set(all_locations.ids)

# ── Build children map ─────────────────────────────────────────────────────
children_of = defaultdict(list)
for loc in all_locations:
    parent_id = loc.location_id.id if loc.location_id.id in internal_ids else 0
    children_of[parent_id].append(loc)

for key in children_of:
    children_of[key].sort(key=lambda l: l.name.lower())

# ── Assign X to leaves sequentially, then propagate to parents ────────────
coords = {}   # loc.id -> (x, y)
leaf_counter = [1]   # mutable counter

def assign(loc, depth):
    children = children_of.get(loc.id, [])
    if not children:
        # leaf: give it the next X slot
        x = leaf_counter[0]
        leaf_counter[0] += 1
    else:
        # recurse first, then center over children
        for child in children:
            assign(child, depth + 1)
        child_xs = [coords[c.id][0] for c in children]
        x = round((min(child_xs) + max(child_xs)) / 2)
    coords[loc.id] = (x, depth + 1)   # +1 so minimum y is 1 (0,0 = not placed)

roots = [loc for loc in all_locations if loc.location_id.id not in internal_ids]
roots.sort(key=lambda l: l.complete_name.lower())

for root in roots:
    assign(root, 0)

# ── Write to DB ────────────────────────────────────────────────────────────
print(f"{'Location':<42} {'x':>4} {'y':>4}")
print("-" * 52)

for loc in sorted(all_locations, key=lambda l: (coords[l.id][1], coords[l.id][0])):
    x, y = coords[loc.id]
    loc.x_pos = x
    loc.y_pos = y
    short = loc.complete_name.replace('WH/Stock/', '')
    print(f"{short:<42} {x:>4} {y:>4}")

env.cr.commit()
print("\nCoordinates saved successfully.")
