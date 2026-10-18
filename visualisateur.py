import argparse
import json
import html
import webbrowser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
AGENTS_PATHS = {
    "seuil": ROOT / "vecteurs" / "agents_seuil",
    "complet": ROOT / "vecteurs" / "agents_complet",
}
OUTPUT_PATH = ROOT / "visualisation_arbres.html"


def compact_node(node: dict[str, Any], node_id: list[int]) -> dict[str, Any]:
    current_id = node_id[0]
    node_id[0] += 1
    children = [compact_node(child, node_id) for child in node.get("children", [])]
    return {
        "id": current_id,
        "samples": node.get("samples", 1),
        "similarity": node.get("merge_similarity"),
        "text": node.get("texte_complet", ""),
        "children": children,
    }


def load_agents(mode: str) -> dict[str, Any]:
    agents: dict[str, Any] = {}
    paths = AGENTS_PATHS if mode == "tous" else {mode: AGENTS_PATHS[mode]}
    for current_mode, directory in paths.items():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            key = f"{current_mode}:{data['relation']}:{data['definitude']}"
            agents[key] = {
                "mode": current_mode,
                "relation": data["relation"],
                "definitude": data["definitude"],
                "examples_count": data.get("examples_count", 0),
                "trees": [compact_node(tree, [0]) for tree in data.get("trees", [])],
            }
    return agents


def generate_html(agents: dict[str, Any], selected: str | None = None) -> str:
    payload = json.dumps(agents, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    selected_json = json.dumps(selected or "")
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Visualisation des arbres symboliques</title>
<style>
:root {{ font-family: system-ui, sans-serif; color: #18212f; background: #f4f6f8; }}
body {{ margin: 0; }}
header {{ padding: 20px 28px; background: #172033; color: white; }}
h1 {{ margin: 0 0 12px; font-size: 22px; }}
.controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
select, button {{ padding: 8px 10px; border-radius: 5px; border: 1px solid #cbd2dc; background: white; }}
main {{ padding: 20px 28px; overflow: auto; }}
#meta {{ margin-bottom: 12px; color: #526071; }}
svg {{ display: block; min-width: 900px; background: white; border: 1px solid #dce2e9; border-radius: 6px; }}
.edge {{ stroke: #aab4c2; stroke-width: 1.5; }}
.node {{ stroke: #344054; stroke-width: 1.5; }}
.merge {{ fill: #b9d8ff; }}
.leaf {{ fill: #d9f1df; }}
text {{ font-size: 12px; fill: #18212f; pointer-events: none; }}
.small {{ font-size: 10px; fill: #526071; }}
.empty {{ padding: 32px; background: white; border: 1px solid #dce2e9; }}
</style>
</head>
<body>
<header>
<h1>Arbres symboliques JDM</h1>
<div class="controls">
<label for="agent">Agent :</label>
<select id="agent"></select>
<button id="all">Vue globale</button>
</div>
</header>
<main>
<div id="meta"></div>
<div id="canvas"></div>
</main>
<script>
const agents = {payload};
const initial = {selected_json};
const select = document.getElementById('agent');
const meta = document.getElementById('meta');
const canvas = document.getElementById('canvas');
const keys = Object.keys(agents).sort();
for (const key of keys) {{
  const option = document.createElement('option');
  option.value = key;
  option.textContent = key;
  select.appendChild(option);
}}
select.value = initial && agents[initial] ? initial : (keys[0] || '');

document.getElementById('all').onclick = () => renderOverview();
select.onchange = () => renderAgent(select.value);

function renderOverview() {{
  meta.textContent = keys.length + ' agents chargés. Sélectionnez un agent pour afficher son arbre.';
  canvas.innerHTML = '<div class="empty">Vue globale : ' + keys.map(k => k + ' (' + agents[k].trees.length + ' arbre(s))').join('<br>') + '</div>';
}}
function label(node) {{
  const score = node.similarity === null ? 'feuille' : 'fusion ' + Number(node.similarity).toFixed(3);
  return '#' + node.id + ' | ' + node.samples + ' ex. | ' + score;
}}
function flatten(root) {{
  const nodes = [], edges = [], leaves = [];
  function visit(node, depth) {{
    node.depth = depth;
    nodes.push(node);
    if (!node.children.length) leaves.push(node);
    for (const child of node.children) {{ edges.push([node, child]); visit(child, depth + 1); }}
  }}
  visit(root, 0);
  return {{nodes, edges, leaves}};
}}
function drawTree(root) {{
  const {{nodes, edges, leaves}} = flatten(root);
  const leafGap = 150, levelGap = 100, width = Math.max(900, leaves.length * leafGap + 80);
  const positions = new Map();
  leaves.forEach((node, index) => positions.set(node.id, {{x: 40 + index * leafGap, y: 50 + node.depth * levelGap}}));
  for (let i = nodes.length - 1; i >= 0; i--) {{
    const node = nodes[i];
    if (!positions.has(node.id)) {{
      const childPositions = node.children.map(c => positions.get(c.id));
      positions.set(node.id, {{x: childPositions.reduce((a, p) => a + p.x, 0) / childPositions.length, y: 50 + node.depth * levelGap}});
    }}
  }}
  const height = Math.max(140, (Math.max(...nodes.map(n => n.depth)) + 1) * levelGap + 50);
  const parts = ['<svg width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + ' ' + height + '">'];
  for (const [parent, child] of edges) {{ const p=positions.get(parent.id), c=positions.get(child.id); parts.push('<line class="edge" x1="'+p.x+'" y1="'+(p.y+18)+'" x2="'+c.x+'" y2="'+(c.y-18)+'"/>'); }}
  for (const node of nodes) {{ const p=positions.get(node.id), leaf=!node.children.length, text=node.text ? '<title>'+escapeHtml(node.text)+'</title>' : ''; parts.push('<g><circle class="node '+(leaf?'leaf':'merge')+'" cx="'+p.x+'" cy="'+p.y+'" r="18"/>'+text+'<text x="'+p.x+'" y="'+(p.y+38)+'" text-anchor="middle">'+label(node)+'</text></g>'); }}
  parts.push('</svg>'); return parts.join('');
}}
function renderAgent(key) {{
  const agent = agents[key]; if (!agent) return;
  meta.textContent = key + ' | ' + agent.examples_count + ' exemples | ' + agent.trees.length + ' arbre(s)';
  canvas.innerHTML = agent.trees.map((tree, i) => '<h3>Arbre ' + (i+1) + '</h3>' + drawTree(tree)).join('');
}}
function escapeHtml(value) {{ return String(value).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c])); }}
if (keys.length) renderAgent(select.value); else renderOverview();
</script>
</body>
</html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualise les arbres appris dans des fichiers HTML/SVG.")
    parser.add_argument("--mode", choices=["seuil", "complet", "tous"], default="tous")
    parser.add_argument("--agent", help="Agent à sélectionner, par exemple r_objet>matiere_0")
    parser.add_argument("--sortie", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--ouvrir", action="store_true", help="Ouvre automatiquement le fichier dans le navigateur.")
    args = parser.parse_args()
    agents = load_agents(args.mode)
    if not agents:
        print("Aucun agent trouvé. Régénérez d'abord les arbres avec evaluateur.py --train.")
        return 1
    selected = None
    if args.agent:
        selected = next(
            (
                key for key, agent in agents.items()
                if args.agent in key
                or args.agent == f"{agent['relation']}_{agent['definitude']}"
            ),
            None,
        )
        if selected is None:
            print(f"Agent introuvable : {args.agent}")
            return 1
    args.sortie.write_text(generate_html(agents, selected), encoding="utf-8")
    print(f"Visualisation créée : {args.sortie}")
    print(f"Agents affichables : {len(agents)}")
    if args.ouvrir:
        webbrowser.open(args.sortie.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
