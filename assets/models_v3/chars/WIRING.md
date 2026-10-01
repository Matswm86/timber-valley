# Wiring the models_v3 characters into CharacterModel.gd

Twelve GLBs with the same file names as `assets/models/chars/` (`character-male-a` ... `character-female-f`),
so Player.gd, Walker.gd, Customer.gd, Shop.gd and World.gd keep their model names. Only
`scripts/CharacterModel.gd` needs to change. Checked by loading the GLB in Godot 4.6 (GLTFDocument, headless).

## Node tree after import
```
character-male-e (Node3D)
  Rig (Node3D, scale 0.35-0.37 baked in the file, so every variant stands 0.80 units tall)
    Skeleton3D
      handslot_r (BoneAttachment3D, bone "handslot.r")   <- created by the importer
        Axe          (MeshInstance3D)  plain axe
        AxeUpgraded  (MeshInstance3D)  gold axe
      Body (MeshInstance3D, skinned)
  AnimationPlayer
```
One material and one embedded 512 px texture per file. Body: about 2,700 tris; each axe: 150 tris.

## What to change
| Item | Kenney (now) | models_v3 |
|---|---|---|
| Path | `res://assets/models/chars/%s.glb` | `res://assets/models_v3/chars/%s.glb` |
| Scale | `SCALE = 2.25` | **keep 2.25**. The rig scale is in the file, so the height is 0.80 x 2.25 = 1.8 m. That is a little taller than Kenney's 1.5 m, but the same on-screen size, because Kenney is boxier. |
| Forward axis | +Z | **+Z**, same as Kenney: no extra rotation |
| Axe | `BoneAttachment3D` on `arm-right` + `tool-axe.glb`, rot (90,0,0), pos (-0.02,-0.12,0.06), scale 1.3 | **Do not build an attachment.** The axes are already in the hand. Use `axe = inst.find_child("Axe", true, false)` and `axe_up = inst.find_child("AxeUpgraded", true, false)`, and hide both in `setup()`. `set_axe_model(upgraded)` then only switches which of the two is visible (keep the chop-only visibility logic). |
| Bone for a custom attachment | `arm-right` | `handslot.r`, the grip point; its children need identity transform. |

## Animation names
| Use | Kenney | models_v3 | Length |
|---|---|---|---|
| idle | `idle` | `Idle` | 1.04 s |
| walk | `walk` | `Walking_A` | 1.04 s |
| run | `sprint` | `Running_A` | 0.79 s |
| chop (standing) | `attack-melee-right` | `1H_Melee_Attack_Slice_Horizontal`: a sideways swing at waist height that hits the trunk. The alternative is `1H_Melee_Attack_Chop`, an overhead swing that reads less like felling. | 1.04 s |
| carry overlay pose | `holding-both` | `Carry_Pose`: one frame, forearms forward in front of the chest | 1 frame |
| extras | - | `PickUp`, `Interact`, `Use_Item` (cashier), `Cheer` (unlock) | |

`Idle`, `Walking_A` and `Running_A` import as non-looping, so set `LOOP_LINEAR` on them as `_build_anims()`
already does for the old names.

## Bone lists for `_compose()`
Bone names keep their dots. Track paths look like `Rig/Skeleton3D:upperarm.l`, so the existing
`ends_with(":" + bone)` test works unchanged (`:hand.r` does not match `:handIK.r`).
- carry-walk / carry-idle: `_compose("Walking_A" / "Idle", "Carry_Pose", ["upperarm.l", "lowerarm.l", "upperarm.r", "lowerarm.r"])`
- chop-walk: `_compose("Walking_A", "1H_Melee_Attack_Slice_Horizontal", ["upperarm.l", "lowerarm.l", "wrist.l", "hand.l", "upperarm.r", "lowerarm.r", "wrist.r", "hand.r", "chest"])`

Full skeleton (41 bones): root, hips, spine, chest, head, upperarm/lowerarm/wrist/hand/handslot .l/.r,
upperleg/lowerleg/foot/toes .l/.r, plus non-deforming IK helpers (kneeIK, heelIK, IK-foot, IK-toe,
control-*, elbowIK, handIK). The helpers have animation tracks but move nothing.

## Suggested roles (already matches the names used in code)
Player `male-e` (2026-10-01: friendly Knight-based lumberjack: brown hair under a mustard knit beanie, red-and-black plaid shirt, raised brows and a smile; the only red and the only cap. Same rig, bone names, `handslot.r` axes, animation names, rig scale 0.3456 and body budget, so no code change). Unused candidates: `character-player-alt-1/3/4.glb` (review sheet `tools/lookdev/player_options.png`); lumberjacks `male-a/c/d`,
`female-a`; haulers `male-b`, `female-b/c/d`; cashier `female-e`; customers any. Every variant has
the axe meshes, so any model can chop.

## Rebuild
`/home/mm/.local/bin/blender -b --python tools/lookdev/build_chars.py [-- name ...]` (source pack:
see SOURCES.md). Colours per variant are in `PLAN` at the top of the script.
