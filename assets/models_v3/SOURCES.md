# models_v3 sources

Look-dev replacements for the Kenney models in the starting area. Same file names as
`assets/models/<kit>/`, so swapping is a path change (`models/` -> `models_v3/`).
Every file is ONE mesh with ONE material and one embedded texture (albedo x height gradient x
baked ambient occlusion, contact shadow included), because `World._multimesh` uses only the first mesh.

`*_far.glb` = 170-triangle variants for the border forest (see docs/DESIGN.md, section 11).

Rebuild: download the two packs into `$LOOKDEV_SRC` (default `/home/mm/MWM/data/lookdev_src`:
`kkf/` = unzipped KayKit Forest free zip, `hexprops/` = the used glTF+bin files from the Medieval
Hexagon repo, plus `hexagons_medieval.png`), then
`/home/mm/.local/bin/blender -b --python tools/lookdev/build_v3.py` and
`python3 tools/lookdev/make_compare.py` (writes tools/lookdev/compare.png).

Round 2 (2026-10-01): broadleaf chop trees keep full Kenney height, with the canopy squeezed in X/Y to at most
1.05x the Kenney width (`sqz` in build_v3.py). Rocks are replaced by own rounded pebbles. Characters were added,
see the table at the end.

Licences: KayKit packs are CC0 1.0 (credit to Kay Lousberg, www.kaylousberg.com, appreciated,
not required). Nothing CC-BY is used, so no credit line is required in the README.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `nature/tree_default.glb` | KayKit Forest Nature Pack: `Tree_1_A_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 530 | 512x512 |
| `nature/tree_oak.glb` | KayKit Forest Nature Pack: `Tree_1_B_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 636 | 512x512 |
| `nature/tree_detailed.glb` | KayKit Forest Nature Pack: `Tree_3_A_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 700 | 512x512 |
| `nature/tree_fat.glb` | KayKit Forest Nature Pack: `Tree_3_B_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 700 | 512x512 |
| `nature/tree_default_dark.glb` | KayKit Forest Nature Pack: `Tree_1_A_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 530 | 512x512 |
| `nature/tree_pineTallA_detailed.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:5:0.46:1.53:0.9:0`), own work | CC0 (released with this repo) | 688 | 512x512 |
| `nature/tree_pineTallB_detailed.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:5:0.46:1.93:0.9:1`), own work | CC0 (released with this repo) | 688 | 512x512 |
| `nature/tree_pineTallC_detailed.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:4:0.56:1.67:1.0:2`), own work | CC0 (released with this repo) | 578 | 512x512 |
| `nature/tree_pineTallD_detailed.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:5:0.56:2.08:1.0:3`), own work | CC0 (released with this repo) | 688 | 512x512 |
| `nature/tree_pineRoundA.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:3:0.74:1.37:1.6:4`), own work | CC0 (released with this repo) | 468 | 512x512 |
| `nature/tree_pineRoundB.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:3:0.64:1.20:1.6:5`), own work | CC0 (released with this repo) | 468 | 512x512 |
| `nature/tree_pineRoundC.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:3:0.58:1.25:1.6:6`), own work | CC0 (released with this repo) | 468 | 512x512 |
| `nature/tree_pineDefaultA.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:4:0.62:1.55:1.2:7`), own work | CC0 (released with this repo) | 578 | 512x512 |
| `nature/tree_pineDefaultB.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:4:0.62:1.55:1.2:8`), own work | CC0 (released with this repo) | 578 | 512x512 |
| `nature/plant_bush.glb` | KayKit Forest Nature Pack: `Bush_1_C_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 168 | 256x256 |
| `nature/plant_bushDetailed.glb` | KayKit Forest Nature Pack: `Bush_1_E_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 300 | 256x256 |
| `nature/grass.glb` | KayKit Forest Nature Pack: `Grass_1_C_Singlesided_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 126 | 128x128 |
| `nature/grass_large.glb` | KayKit Forest Nature Pack: `Grass_1_D_Singlesided_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 168 | 128x128 |
| `nature/grass_leafs.glb` | KayKit Forest Nature Pack: `Grass_1_B_Singlesided_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 42 | 128x128 |
| `nature/rock_smallA.glb` | Built in tools/lookdev/build_v3.py (`proc:pebbles:1`), own work: rounded warm-grey pebbles (round 2) | CC0 (released with this repo) | 144 | 256x256 |
| `nature/rock_smallC.glb` | Built in tools/lookdev/build_v3.py (`proc:pebbles:2`), own work: rounded warm-grey pebbles (round 2) | CC0 (released with this repo) | 288 | 256x256 |
| `nature/rock_smallD.glb` | Built in tools/lookdev/build_v3.py (`proc:pebbles:3`), own work: rounded warm-grey pebbles (round 2) | CC0 (released with this repo) | 288 | 256x256 |
| `nature/rock_largeA.glb` | Built in tools/lookdev/build_v3.py (`proc:pebbles:4`), own work: rounded warm-grey pebbles (round 2) | CC0 (released with this repo) | 432 | 256x256 |
| `nature/flower_redA.glb` | Built in tools/lookdev/build_v3.py (`proc:flower_red`), own work | CC0 (released with this repo) | 132 | 128x128 |
| `nature/flower_redC.glb` | Built in tools/lookdev/build_v3.py (`proc:flower_red`), own work | CC0 (released with this repo) | 132 | 128x128 |
| `nature/flower_yellowA.glb` | Built in tools/lookdev/build_v3.py (`proc:flower_yellow`), own work | CC0 (released with this repo) | 132 | 128x128 |
| `nature/flower_yellowB.glb` | Built in tools/lookdev/build_v3.py (`proc:flower_white`), own work | CC0 (released with this repo) | 132 | 128x128 |
| `nature/mushroom_redGroup.glb` | Built in tools/lookdev/build_v3.py (`proc:mushrooms_red`), own work | CC0 (released with this repo) | 174 | 128x128 |
| `nature/mushroom_tanGroup.glb` | Built in tools/lookdev/build_v3.py (`proc:mushrooms_tan`), own work | CC0 (released with this repo) | 174 | 128x128 |
| `nature/stump_roundDetailed.glb` | Built in tools/lookdev/build_v3.py (`proc:stump`), own work | CC0 (released with this repo) | 356 | 256x256 |
| `nature/log_stackLarge.glb` | Built in tools/lookdev/build_v3.py (`proc:log_stack`), own work | CC0 (released with this repo) | 936 | 256x256 |
| `nature/campfire_logs.glb` | Built in tools/lookdev/build_v3.py (`proc:campfire`), own work | CC0 (released with this repo) | 640 | 256x256 |
| `nature/fence_simple.glb` | Built in tools/lookdev/build_v3.py (`proc:fence`), own work | CC0 (released with this repo) | 768 | 256x256 |
| `survival/barrel.glb` | KayKit Medieval Hexagon Pack: `barrel.gltf` - https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0 | CC0 (Kay Lousberg) | 240 | 256x256 |
| `survival/box-large.glb` | Built in tools/lookdev/build_v3.py (`proc:crate`), own work | CC0 (released with this repo) | 260 | 256x256 |
| `survival/signpost.glb` | Built in tools/lookdev/build_v3.py (`proc:signpost`), own work | CC0 (released with this repo) | 272 | 256x256 |
| `nature/tree_default_far.glb` | KayKit Forest Nature Pack: `Tree_1_A_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 169 | 256x256 |
| `nature/tree_oak_far.glb` | KayKit Forest Nature Pack: `Tree_1_B_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 169 | 256x256 |
| `nature/tree_detailed_far.glb` | KayKit Forest Nature Pack: `Tree_1_B_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 169 | 256x256 |
| `nature/tree_fat_far.glb` | KayKit Forest Nature Pack: `Tree_1_A_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 169 | 256x256 |
| `nature/tree_default_dark_far.glb` | KayKit Forest Nature Pack: `Tree_1_A_Color1.gltf` - https://kaylousberg.itch.io/kaykit-forest (KayKit Forest Nature Pack 1.0, FREE tier) | CC0 (Kay Lousberg) | 169 | 256x256 |
| `nature/tree_pineTallA_detailed_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:5:0.46:1.53:0.9:0`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineTallB_detailed_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:5:0.46:1.93:0.9:1`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineTallC_detailed_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:4:0.56:1.67:1.0:2`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineTallD_detailed_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:5:0.56:2.08:1.0:3`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineRoundA_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:3:0.74:1.37:1.6:4`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineRoundB_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:3:0.64:1.20:1.6:5`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineRoundC_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:3:0.58:1.25:1.6:6`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineDefaultA_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:4:0.62:1.55:1.2:7`), own work | CC0 (released with this repo) | 170 | 256x256 |
| `nature/tree_pineDefaultB_far.glb` | Built in tools/lookdev/build_v3.py (`proc:pine:4:0.62:1.55:1.2:8`), own work | CC0 (released with this repo) | 170 | 256x256 |

## Characters (models_v3/chars)

Built by `tools/lookdev/build_chars.py` from the KayKit Adventurers pack (git clone into
`$LOOKDEV_SRC/KayKit-Character-Pack-Adventures-1.0`). Hats, helmets, capes and weapons are removed. The gradient
atlas is recoloured per variant to workwear colours. The body is joined into one skinned mesh and decimated
(the head keeps 90% of its triangles). Albedo x height gradient x AO is baked from the full-res source into
one 512 px texture. The pack's 1H axe (from `Barbarian.glb`, scaled 0.75) and a gold copy are parented to
bone `handslot.r`. `Carry_Pose` is own work (CC0). Animations kept: Idle, Walking_A, Running_A,
1H_Melee_Attack_Slice_Horizontal, 1H_Melee_Attack_Chop, PickUp, Interact, Use_Item, Cheer, Carry_Pose.
Wiring for Godot: `chars/WIRING.md`. The axe tris count once, because only one axe is visible at a time.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `chars/character-male-e.glb` (player, 2026-10-01: own face edit + own knit beanie + procedural plaid) | KayKit Character Pack: Adventurers 1.0, `Knight.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2695 body + 2x150 axe | 512x512 |
| `chars/character-male-a.glb` | KayKit Character Pack: Adventurers 1.0, `Barbarian.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2695 body + 2x150 axe | 512x512 |
| `chars/character-male-b.glb` | KayKit Character Pack: Adventurers 1.0, `Knight.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2694 body + 2x150 axe | 512x512 |
| `chars/character-male-c.glb` | KayKit Character Pack: Adventurers 1.0, `Knight.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2694 body + 2x150 axe | 512x512 |
| `chars/character-male-d.glb` | KayKit Character Pack: Adventurers 1.0, `Mage.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2694 body + 2x150 axe | 512x512 |
| `chars/character-male-f.glb` | KayKit Character Pack: Adventurers 1.0, `Mage.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2694 body + 2x150 axe | 512x512 |
| `chars/character-female-a.glb` | KayKit Character Pack: Adventurers 1.0, `Rogue.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2691 body + 2x150 axe | 512x512 |
| `chars/character-female-b.glb` | KayKit Character Pack: Adventurers 1.0, `Rogue.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2691 body + 2x150 axe | 512x512 |
| `chars/character-female-c.glb` | KayKit Character Pack: Adventurers 1.0, `Rogue_Hooded.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2697 body + 2x150 axe | 512x512 |
| `chars/character-female-d.glb` | KayKit Character Pack: Adventurers 1.0, `Rogue.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2691 body + 2x150 axe | 512x512 |
| `chars/character-female-e.glb` | KayKit Character Pack: Adventurers 1.0, `Rogue.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2691 body + 2x150 axe | 512x512 |
| `chars/character-player-alt-1.glb` (candidate, Knight, plaid, face edit) | KayKit Character Pack: Adventurers 1.0, `Knight.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2694 body + 2x150 axe | 512x512 |
| `chars/character-player-alt-3.glb` (candidate, Mage, plaid, face edit) | KayKit Character Pack: Adventurers 1.0, `Mage.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2694 body + 2x150 axe | 512x512 |
| `chars/character-player-alt-4.glb` (candidate, Barbarian, own beanie, face edit) | KayKit Character Pack: Adventurers 1.0, `Barbarian.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2692 body + 2x150 axe | 512x512 |
| `chars/character-female-f.glb` | KayKit Character Pack: Adventurers 1.0, `Rogue_Hooded.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2697 body + 2x150 axe | 512x512 |

## M1 Birch Bend + item models (models_v3/birch, models_v3/items), icons, ground tiles, imposters

Everything in this section is own work built from Blender primitives, noise and Voronoi textures in this repo,
released CC0 with the repo. No third-party asset, texture or font is inside these files, so no credit line is needed.
Rebuild: `/home/mm/.local/bin/blender -b --python tools/lookdev/build_m1.py` (models, same bake as build_v3.py),
`python3 tools/lookdev/make_icons_m1.py` (icons via `um render3d` + `um sprite fit`),
`tools/lookdev/make_ground_m1.sh` (ground via own Blender material + `um sprite seamless` / `tile-preview`),
`python3 tools/lookdev/make_imposters_m1.py` (border-forest atlas via `um render3d` + `um sprite sheet`),
`python3 tools/lookdev/make_compare_m1.py` (review sheet `tools/lookdev/compare_m1.png`).
Use and placement: `assets/models_v3/ASSETS_M1.md`.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `birch/tree_birchA.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 693 | 512x512 |
| `birch/tree_birchB.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 670 | 512x512 |
| `birch/tree_birchC.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 694 | 512x512 |
| `birch/tree_birchA_far.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `birch/tree_birchB_far.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `birch/tree_birchC_far.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 180 | 256x256 |
| `birch/stump_birch.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 356 | 256x256 |
| `birch/log_stack_birch.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 936 | 256x256 |
| `birch/reeds.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 198 | 128x128 |
| `birch/lilypads.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 432 | 128x128 |
| `birch/veneer_lathe.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 1552 | 512x512 |
| `birch/veneer_lathe_log.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 164 | 256x256 |
| `birch/plywood_press.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 1428 | 512x512 |
| `birch/plywood_press_plate.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 152 | 128x128 |
| `birch/boat_workshop.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 1324 | 512x512 |
| `birch/riverside_office.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 1556 | 512x512 |
| `birch/barge.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 1796 | 512x512 |
| `birch/barge_landing.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 708 | 512x512 |
| `birch/flume_straight.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 308 | 256x256 |
| `birch/flume_chute.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 652 | 256x256 |
| `birch/flume_end.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 440 | 256x256 |
| `birch/boathouse.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 1448 | 512x512 |
| `items/item_log.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 140 | 256x256 |
| `items/item_plank.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 108 | 256x256 |
| `items/item_chair.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 252 | 256x256 |
| `items/item_table.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 220 | 256x256 |
| `items/item_bookcase.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 376 | 256x256 |
| `items/item_birch_log.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 140 | 256x256 |
| `items/item_veneer.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 128 | 128x128 |
| `items/item_plywood.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 108 | 256x256 |
| `items/item_canoe.glb` | Built in tools/lookdev/build_m1.py, own work | CC0 (released with this repo) | 548 | 256x256 |
| `assets/icons/*.png` (9 items x 256/128/64) | Rendered from the `items/*.glb` above (tools/lookdev/make_icons_m1.py) | CC0 (released with this repo) | - | - |
| `assets/textures/ground/{grass_v1,grass_birch,dirt_path}.png` | Own procedural Blender material (tools/lookdev/make_ground_m1.py) | CC0 (released with this repo) | - | 512x512 |
| `assets/textures/imposters/border_trees_atlas.png` | Rendered from `nature/*_far.glb` (KayKit-derived CC0 and own pines) and `birch/*_far.glb` | CC0 (Kay Lousberg for the KayKit-derived trees; rest own work) | 2 per card | 2048x2048 |

## Leftover replacements (models_v3/shared, models_v3/home), road tile (2026-10-01)

Own work from Blender primitives in `tools/lookdev/build_leftover.py` (same bake as build_v3.py / build_m1.py), released CC0
with the repo. No third-party asset, texture or font is inside these files. Placement: `assets/models_v3/ASSETS_LEFTOVER.md`.
They replace the last Kenney models loaded by scripts/ (crane, truck-flat, bridge_wood, chest, structure-yellow-tall,
workbench, workbench-grind, signpost-single, chair, machine-window, screen-small, cog-a, lever-single, machine-fortified,
machine, hopper-square, robot-arm-a/b, bench, loungeChair). The Kenney files stay in `assets/models/` (CC0) until the code stops loading them.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `shared/belt_rails.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 300 | 128x128 |
| `home/saw_blade.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 496 | 128x128 |
| `shared/belt_legs.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 220 | 128x128 |
| `shared/belt_end.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 460 | 128x128 |
| `shared/palisade_post.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 56 | 128x128 |
| `shared/bridge_river.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1788 | 512x512 |
| `shared/shop_counter.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 308 | 256x256 |
| `shared/shop_till.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 668 | 256x256 |
| `shared/market_canopy.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1424 | 256x256 |
| `shared/truck_flatbed.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1796 | 512x512 |
| `shared/truck_dock.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 588 | 256x256 |
| `home/sawmill_body_orange.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1412 | 512x512 |
| `home/sawmill_body_green.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1412 | 512x512 |
| `home/office_hut.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1592 | 512x512 |
| `home/carpentry_shed.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1704 | 512x512 |
| `home/cnc_router.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1232 | 512x512 |
| `home/cnc_cog.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 360 | 128x128 |
| `home/bookcase_factory.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1820 | 512x512 |
| `home/factory_arm.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 608 | 128x128 |
| `home/grand_lodge.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 2228 | 512x512 |
| `home/lodge_windows.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 8 | emissive material, no texture |
| `home/megasaw_body.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 1520 | 512x512 |
| `home/megasaw_crane.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 844 | 256x256 |
| `home/crane_hook.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 208 | 128x128 |
| `home/road_sign.glb` | Built in tools/lookdev/build_leftover.py, own work | CC0 (released with this repo) | 580 | 256x256 |
| `assets/textures/ground/road_tile.png` | Own numpy noise + dash (tools/lookdev/make_road_tile.py) | CC0 (released with this repo) | - | 512x512 |

## M2 Maple Highlands (models_v3/maple, models_v3/items), icons, ground, imposters (2026-10-01)

Own work from Blender primitives in `tools/lookdev/build_m2.py`, released CC0 with the repo. No third-party asset inside.
Exception: cells 12-15 of the imposter atlas render `nature/tree_pineTallB_detailed_far.glb` (own pine, CC0).
Placement: `assets/models_v3/ASSETS_M2.md`.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `maple/tree_mapleA.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 686 | 512x512 |
| `maple/tree_mapleB.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 686 | 512x512 |
| `maple/tree_mapleC.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 686 | 512x512 |
| `maple/tree_mapleA_far.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `maple/tree_mapleB_far.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `maple/tree_mapleC_far.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `maple/stump_maple.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 428 | 256x256 |
| `maple/log_stack_maple.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 936 | 256x256 |
| `maple/leaf_pile.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 296 | 128x128 |
| `maple/bush_autumn.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 218 | 256x256 |
| `items/item_maple_log.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 140 | 256x256 |
| `items/item_beam.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 108 | 256x256 |
| `items/item_floorboard.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 100 | 128x128 |
| `items/item_cabin_kit.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 724 | 256x256 |
| `maple/beam_saw.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1008 | 512x512 |
| `maple/beam_saw_blade.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 464 | 128x128 |
| `maple/planer_mill.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1248 | 512x512 |
| `maple/planer_roller.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 116 | 128x128 |
| `maple/kit_factory.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 2548 | 512x512 |
| `maple/kit_factory_press.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 92 | 128x128 |
| `maple/forklift.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 928 | 256x256 |
| `maple/rail_straight_4m.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 276 | 256x256 |
| `maple/rail_bumper.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 348 | 128x128 |
| `maple/handcar.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 444 | 256x256 |
| `maple/handcar_tile.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 264 | 128x128 |
| `maple/handcar_stop.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 532 | 256x256 |
| `maple/lantern_post.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 144 | 128x128 |
| `maple/train_loco.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1020 | 512x512 |
| `maple/train_wagon.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 584 | 256x256 |
| `maple/rail_platform.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 676 | 512x512 |
| `maple/highland_office.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 708 | 512x512 |
| `maple/market_canopy_teal.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1424 | 256x256 |
| `maple/house_cottage.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1192 (stage1 88, stage2 440, stage3 320, stage4 344) | 512x512 |
| `maple/house_farmhouse.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1328 (stage1 88, stage2 440, stage3 320, stage4 480) | 512x512 |
| `maple/house_barn.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1268 (stage1 44, stage2 440, stage3 388, stage4 396) | 512x512 |
| `maple/house_school.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1400 (stage1 88, stage2 440, stage3 456, stage4 416) | 512x512 |
| `maple/house_inn.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1572 (stage1 88, stage2 528, stage3 632, stage4 324) | 512x512 |
| `maple/clock_tower.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 1816 (stage1 88, stage2 352, stage3 400, stage4 568, stage5 300, stage6 108) | 512x512 |
| `maple/highland_gate.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 824 | 512x512 |
| `maple/highland_gate_doors.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 392 | 256x256 |
| `maple/build_plot.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 398 | 128x128 |
| `maple/beam_cart.glb` | Built in tools/lookdev/build_m2.py, own work | CC0 (released with this repo) | 632 | 256x256 |
| `assets/icons/{maple_log,beam,floorboard,cabin_kit}{,_128,_64}.png` | Rendered from the item GLBs (tools/lookdev/make_icons_m2.py) | CC0 (released with this repo) | - | - |
| `assets/textures/ground/grass_maple.png` | Own procedural Blender material (tools/lookdev/make_ground_m2.py) | CC0 (released with this repo) | - | 512x512 |
| `assets/textures/imposters/border_trees_atlas_m2.png` | Rendered from `maple/*_far.glb` + `nature/tree_pineTallB_detailed_far.glb` (tools/lookdev/make_imposters_m2.py) | CC0 (released with this repo) | 2 per card | 1024x1024 |

## M3 Redwood Coast (models_v3/redwood, models_v3/items), icons, ground, imposters (2026-10-01)

Own work from Blender primitives in `tools/lookdev/build_m3.py` (helpers `tools/lookdev/m345_lib.py`), released CC0 with
the repo. No third-party asset inside. `redwood/forklift_navy.glb`, `handcar_navy.glb` and `handcar_stop_navy.glb` are
the M2 builders (`build_m2.py`, own work) with the accent colour swapped.
Exception: cells 12-15 of the imposter atlas render `nature/tree_pineTallB_detailed_far.glb` (own pine, CC0).
Placement: `assets/models_v3/ASSETS_M3.md`.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `redwood/tree_redwoodA.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 642 | 512x512 |
| `redwood/tree_redwoodA_far.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `items/item_mast.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 308 | 256x256 |
| `redwood/cargo_ship.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1740 | 512x512 |
| `redwood/ship_hull.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 2412 (stage1 914, stage2 248, stage3 656, stage4 594) | 512x512 |
| `redwood/lighthouse.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 2012 (stage1 520, stage2 232, stage3 212, stage4 152, stage5 604, stage6 292) | 512x512 |
| `redwood/tree_redwoodB.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 642 | 512x512 |
| `redwood/tree_redwoodC.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 598 | 512x512 |
| `redwood/tree_redwoodB_far.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `redwood/tree_redwoodC_far.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 173 | 256x256 |
| `redwood/stump_redwood.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 374 | 256x256 |
| `redwood/log_stack_redwood.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 580 | 256x256 |
| `redwood/dune_grass.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 186 | 128x128 |
| `redwood/driftwood.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 63 | 128x128 |
| `redwood/beach_rock.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 100 | 256x256 |
| `items/item_red_log.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 140 | 256x256 |
| `items/item_timber.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 120 | 256x256 |
| `items/item_deckboard.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 80 | 128x128 |
| `redwood/redwood_mill.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1248 | 512x512 |
| `redwood/redwood_mill_blade.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 516 | 128x128 |
| `redwood/deck_saw.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1048 | 512x512 |
| `redwood/deck_saw_gang.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 708 | 128x128 |
| `redwood/mast_lathe.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1176 | 512x512 |
| `redwood/mast_lathe_log.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 220 | 256x256 |
| `redwood/log_skidder.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1624 | 256x256 |
| `redwood/forklift_navy.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 928 | 256x256 |
| `redwood/fishing_boat.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 592 | 256x256 |
| `redwood/pier_straight_4m.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 896 | 256x256 |
| `redwood/pier_end.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1668 | 256x256 |
| `redwood/order_board.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 504 | 256x256 |
| `redwood/dock_crane.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 140 | 128x128 |
| `redwood/dock_crane_jib.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 312 | 256x256 |
| `redwood/slipway.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1484 | 512x512 |
| `redwood/harbor_office.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1028 | 512x512 |
| `redwood/market_canopy_navy.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 1424 | 256x256 |
| `redwood/crossing_post.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 564 | 256x256 |
| `redwood/crossing_arm.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 384 | 128x128 |
| `redwood/crossing_closed.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 620 | 128x128 |
| `redwood/handcar_stop_navy.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 532 | 256x256 |
| `redwood/buoy.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 196 | 128x128 |
| `redwood/fish_crates.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 224 | 128x128 |
| `redwood/anchor_prop.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 276 | 128x128 |
| `redwood/bollard.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 188 | 128x128 |
| `redwood/harbor_lamp.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 172 | 128x128 |
| `redwood/handcar_navy.glb` | Built in tools/lookdev/build_m3.py, own work | CC0 (released with this repo) | 444 | 256x256 |
| `assets/icons/{red_log,timber,deckboard,mast}{,_128,_64}.png` | Rendered from the item GLBs (tools/lookdev/make_icons_m345.py) | CC0 (released with this repo) | - | - |
| `assets/textures/ground/grass_coast.png`, `sand_beach.png` | Own procedural Blender material (tools/lookdev/make_ground_m345.py) | CC0 (released with this repo) | - | 512x512 |
| `assets/textures/imposters/border_trees_atlas_m3.png` | Rendered from `redwood/*_far.glb` + `nature/tree_pineTallB_detailed_far.glb` (tools/lookdev/make_imposters_m345.py) | CC0 (released with this repo) | 2 per card | 1024x1024 |

## M4 Frost Peaks (models_v3/frost, models_v3/items), icons, ground, imposters (2026-10-03)

Own work from Blender primitives in `tools/lookdev/build_m4.py` (helpers `tools/lookdev/m345_lib.py`), released CC0 with
the repo. No third-party asset inside. `frost/rail_platform_alpine.glb`, `handcar_alpine.glb` and
`handcar_stop_alpine.glb` are the M2 builders (`build_m2.py`, own work) with the accent swapped and snow added.
Placement: `assets/models_v3/ASSETS_M4.md`.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `frost/tree_frostfirA.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 661 | 512x512 |
| `frost/tree_frostfirB.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 661 | 512x512 |
| `frost/tree_frostfirC.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 513 | 512x512 |
| `frost/tree_frostfirD.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 661 | 512x512 |
| `frost/tree_frostfirA_far.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 183 | 256x256 |
| `frost/tree_frostfirB_far.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 183 | 256x256 |
| `frost/tree_frostfirC_far.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 183 | 256x256 |
| `frost/tree_frostfirD_far.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 183 | 256x256 |
| `frost/stump_frost.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 248 | 256x256 |
| `frost/log_stack_frost.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 990 | 256x256 |
| `frost/snow_drift.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 128 | 128x128 |
| `frost/snow_rock.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 160 | 256x256 |
| `frost/snow_bush.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 120 | 128x128 |
| `items/item_frost_log.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 200 | 256x256 |
| `items/item_dry_lumber.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 132 | 128x128 |
| `items/item_skis.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 160 | 256x256 |
| `items/item_sled.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 180 | 256x256 |
| `items/item_guitar.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 328 | 256x256 |
| `frost/drying_kiln.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1204 | 512x512 |
| `frost/kiln_door.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 392 | 128x128 |
| `frost/kiln_glow.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 36 | none (emissive colour) |
| `frost/ski_workshop.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1468 | 512x512 |
| `frost/ski_press.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 84 | 128x128 |
| `frost/sled_workshop.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1936 | 512x512 |
| `frost/sled_workshop_arm.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 152 | 128x128 |
| `frost/luthier_workshop.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 2328 | 512x512 |
| `frost/luthier_sander.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 124 | 128x128 |
| `frost/snowcat.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1436 | 256x256 |
| `frost/mountain_loco.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1224 | 512x512 |
| `frost/mountain_wagon.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 496 | 256x256 |
| `frost/rail_platform_alpine.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 784 | 512x512 |
| `frost/cablecar_station_bottom.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 572 | 512x512 |
| `frost/cablecar_station_top.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 660 | 512x512 |
| `frost/cablecar_bullwheel.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 236 | 128x128 |
| `frost/cablecar_gondola.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 584 | 256x256 |
| `frost/cablecar_cable_1m.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 20 | 64x64 |
| `frost/cablecar_chain.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 200 | 128x128 |
| `frost/mountain_office.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1376 | 512x512 |
| `frost/market_canopy_alpine.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1424 | 256x256 |
| `frost/ski_lodge.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 1308 | 512x512 |
| `frost/handcar_stop_alpine.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 640 | 256x256 |
| `frost/handcar_alpine.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 444 | 256x256 |
| `frost/summit_observatory.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 2812 (stage1 624, stage2 300, stage3 632, stage4 584, stage5 484, stage6 188) | 512x512 |
| `frost/ski_rack.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 720 | 256x256 |
| `frost/snowman.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 608 | 128x128 |
| `frost/alpine_lamp.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 192 | 128x128 |
| `frost/firewood_snow.glb` | Built in tools/lookdev/build_m4.py, own work | CC0 (released with this repo) | 620 | 256x256 |
| `assets/icons/{frost_log,dry_lumber,skis,sled,guitar}{,_128,_64}.png` | Rendered from the item GLBs (tools/lookdev/make_icons_m345.py) | CC0 (released with this repo) | - | - |
| `assets/textures/ground/snow_frost.png`, `snow_packed.png` | Own procedural Blender material (tools/lookdev/make_ground_m345.py) | CC0 (released with this repo) | - | 512x512 |
| `assets/textures/imposters/border_trees_atlas_m4.png` | Rendered from `frost/*_far.glb` (tools/lookdev/make_imposters_m345.py) | CC0 (released with this repo) | 2 per card | 1024x1024 |

## M5 Grand Timber Station (models_v3/station), ground, imposters (2026-10-03)

Own work from Blender primitives in `tools/lookdev/build_m5.py` (helpers `tools/lookdev/m345_lib.py`), released CC0 with
the repo. No third-party asset inside. `station/handcar_stop_station.glb` is the M2 builder with the accent swapped.
Exception: cells 8-15 of the imposter atlas render `maple/tree_mapleA_far.glb` and `nature/tree_default_far.glb` (own, CC0).
Placement: `assets/models_v3/ASSETS_M5.md`.

| File | Source | Licence | Tris | Texture |
|---|---|---|---|---|
| `station/grand_station.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 2940 (stage1 248, stage2 992, stage3 216, stage4 556, stage5 612, stage6 316) | 512x512 |
| `station/station_plot.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 652 | 256x256 |
| `station/platform_slot_v1.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 492 | 256x256 |
| `station/platform_slot_v2.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 492 | 256x256 |
| `station/platform_slot_v3.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 492 | 256x256 |
| `station/platform_slot_v4.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 492 | 256x256 |
| `station/platform_slot_v5.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 492 | 256x256 |
| `station/rail_bridge_8m.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 788 | 256x256 |
| `station/rail_road_crossing_4m.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 192 | 256x256 |
| `station/express_loco.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 1544 | 512x512 |
| `station/express_tender.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 736 | 256x256 |
| `station/express_coach.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 892 | 256x256 |
| `station/tree_station_lime.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 577 | 512x512 |
| `station/tree_station_cone.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 321 | 512x512 |
| `station/tree_station_lime_far.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 103 | 256x256 |
| `station/tree_station_cone_far.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 103 | 256x256 |
| `station/station_bench.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 396 | 128x128 |
| `station/clock_post.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 388 | 128x128 |
| `station/flower_planter.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 384 | 128x128 |
| `station/luggage_cart.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 368 | 128x128 |
| `station/station_lamp.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 352 | 128x128 |
| `station/handcar_stop_station.glb` | Built in tools/lookdev/build_m5.py, own work | CC0 (released with this repo) | 532 | 256x256 |
| `assets/textures/ground/station_paving.png` | Own procedural Blender material (tools/lookdev/make_ground_m345.py) | CC0 (released with this repo) | - | 512x512 |
| `assets/textures/imposters/border_trees_atlas_m5.png` | Rendered from `station/*_far.glb`, `maple/tree_mapleA_far.glb`, `nature/tree_default_far.glb` (tools/lookdev/make_imposters_m345.py) | CC0 (released with this repo) | 2 per card | 1024x1024 |
