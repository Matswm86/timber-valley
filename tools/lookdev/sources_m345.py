"""Print the SOURCES.md table rows for one region from its build report (tris, texture size, stage split).
  python3 tools/lookdev/sources_m345.py m3 >> assets/models_v3/SOURCES.md   (after the section header)"""
import json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
reg = sys.argv[1]
rep = json.load(open(f"{REPO}/tools/lookdev/build_{reg}_report.json"))
for name, r in rep.items():
    if "error" in r:
        continue
    tris = str(r["tris"])
    if r.get("stages"):
        tris += " (" + ", ".join(f"{k} {v}" for k, v in r["stages"].items()) + ")"
    tex = f"{r['tex']}x{r['tex']}" if r["tex"] else "none (emissive colour)"
    print(f"| `{r['folder']}/{name}.glb` | Built in tools/lookdev/build_{reg}.py, own work | CC0 (released with this repo) | {tris} | {tex} |")
