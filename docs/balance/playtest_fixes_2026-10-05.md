# Playtest fixes (2026-10-05): Redwood carriers, station guidance, tables belt, music

Mats playtested the APK built from ab612ae. All numbers are my measurements with
`tests/pacing_probe.gd`, the screenshot bot or ffmpeg; nothing is modelled.

## 1. Redwood Coast: "red logs pile up, customers wait, nobody delivers"

**Root cause.** Nothing carried timber from the mill to the Harbor counter before the harbor
forklift (pad 12). The crews fill the mill, its output fills, and only the player delivers.
Scripted player, crossing -> forklift, carried-in income 3/3/3 ("model") and none ("low"):

| | Before (model / low) | After, 1 carrier (model / low) | After, 2 carriers, shipped (model / low) |
|---|---|---|---|
| Shoppers at an empty timber counter (% of shopper time) | 52 / 54 | 26 / 27 | 23 / 25 |
| Mill input full (% of time) | 84.6 / 82.1 | 76.4 / 78.6 | 68.7 / 71.5 |
| Mill output full (% of time) | 69.7 / 74.8 | 43.2 / 48.4 | 18.5 / 27.5 |
| Timber sold | 325 / 473 | 908 / 1,285 | 1,356 / 1,783 |
| Redwood earnings to the forklift | $34K / $49K | $95K / $135K | $141K / $187K |
| Worker idle (%) | 92.8 / 93.0 | 59.2 / 60.2 | 40.9 / 43.8 |
| Crossing -> forklift | 802 s / 1,182 s | 792 s / 1,136 s | 753 s / 1,070 s |

The empty-counter share covers the whole run, including the first ~3 min before the carriers can
be bought (pads redmill .. jack1 still rely on the player).

**Fix.** New pad `r4_hauler1` "Hire 2 Timber Carriers", $50,000, requires r4_jack1 (cheapest-first
players buy it right after the first lumberjack). Two plain haulers, mill output -> timber counter
(`Balance.TIMBER_CARRIERS = 2`; one alone was busy 100% of the time). They stand down when
`r4_forklift` is bought: while they kept running, the shipwrights got too little timber and no
ship launched in the screenshot bot's 600 s run. Whole valley (scripted player, model income):
45.1 min -> 44.0 min; Lighthouse done 167 s after its pad (unchanged).

## 2. Grand Timber Station: "buy the entry, then nothing happens"

**Root cause: a feedback gap, not a broken unlock.** Buying `cap_station` does build everything
(station plot behind the Home Valley north wall, express rail, five platform sites, five porters).
But right after the purchase there was only a "Grand Timber Station!" toast: the plot is hidden
behind the palisade, the guide arrow disappears (no gateway left), and the hint pill is empty.
Each platform only fills while the player stands in its valley (porters work only while their
valley is awake), and the game never said so. Screenshot bot before the fix:
`m5/06_station_site_rail` shows the toast, no arrow, no hint.

**Fix (GrandStation.gd, World.gd).**
- About 1.2 s after the purchase: toast "Fill one platform in every valley!", and the camera
  glides to the Home Valley platform (its sign shows "BOOKCASES 0/120") and back.
- While the station is unfinished, the guide arrow points at the current valley's platform, or at
  the valley's handcar stop when that platform is full. The hint pill says what to do: "Station
  0/5: Bookcases 0/120 platform", "... stay here" once at the platform, "Station 3/5: handcar to
  Maple Highlands" when the next platform is elsewhere.
- Bot check at 5 s after the purchase: `M5 STATION GUIDE 5s hint='Station 0/5: Bookcases 0/120
  platform' arrow=(-18.0, 0.0, 8.0) guide_visible=true PASS`.

## 3. Home Valley: conveyor for tables

New pad `belt_tables` "Conveyor: Tables to Market", $800 (between the chair belt $650 and the
mega-saw belt $1,000), requires hauler4 + belt_chairs, added to the Grand Lodge requirements.
There is no straight way from the CNC to the market: the Mega Sawmill blocks the middle, the
carpentry and the chair belt its west side, the mega-saw belt and the road its east side. The belt
runs west of the carpentry and bridges the Sawmill 2 belt and the chair belt on short ramps
(`World.V1_BELT_TABLES`; `Conveyor` builds upright, stretched legs for raised points; flat belts are
unchanged). Saves that already own the Lodge keep it (migration test passes); a save before the
Lodge now also needs the tables belt for it. The 60 s probe: 56 tables arrived on the counter.
`unlocks_regions.csv` holds no Valley 1 rows, so there is nothing to mirror there.

## 4. Music

**Root cause: the track is in the APK and does play, but a phone speaker barely reproduces it.**
- The CI APK (2026-10-04, ab612ae) contains `music.ogg` and `ambience.ogg` (imported streams +
  remaps); `sound_on` defaults to true; Sfx starts both loops at boot.
- The old track: 50 s, -19.0 dB RMS, played at -9 dB (about -28 dB in game), while the constant
  effects run about -22 dB (chop -18.5 dB RMS at -4 dB). And 67% of its energy was below 150 Hz,
  88% below 300 Hz, which phone speakers barely play: only about 12% of it was audible on a phone.

**Fix.**
- `tools/make_music.py` (music part rewritten, `--only music|ambience|all`, default music): a
  150 s loop (40 bars, 64 BPM) of soft pads, a quiet bass, a slow e-piano arpeggio and sparse
  bells, no percussion, voiced for phone speakers: 63% of the energy above 300 Hz, 1.4% below 150
  Hz, RMS -12.6 dB, peak -2.3 dB, loop seam step 0.022 (smaller than ordinary steps inside the
  track, 0.07 at the 99.99th percentile). Procedural, no copyrighted audio.
- `Sfx.gd`: `MUSIC_DB = -16` (about -29 dB RMS in game: low, under the effects, now mostly
  audible), `AMBIENCE_DB = -18` (ambience about -40 dB, under the music; was -12).
- Music on/off switch in the menu next to Sound (`Game.music_on`, saved, default on; old saves
  without the key get music on).

## Verification

Android lint PASS; headless load 0 script errors; migration test PASS. Screenshot bot in a
private copy: shots, m2, m4 0 errors / 0 FAIL. m3 and m5, run alone side by side with ab612ae:
m3 "AUTOMATION launches=2 orders=4" at 581 s (ab612ae 580 s), m5 FINISH PASS twice (ab612ae PASS).
Run while other Godot processes loaded the CPU, m3 missed its 600 s budget (1 launch) and m5's
Birch Bend platform missed its 10-frame window once: both checks are timing-sensitive, on
ab612ae as well.

## Not verified

- Not tested on a physical phone, including how loud the new music sounds on its speaker.
- The empty-counter share before the carriers are bought is unchanged (pads before r4_jack1).
