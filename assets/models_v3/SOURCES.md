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
| `chars/character-male-e.glb` | KayKit Character Pack: Adventurers 1.0, `Barbarian.glb` - https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0 (commit 672074b) | CC0 (Kay Lousberg) | 2695 body + 2x150 axe | 512x512 |
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
