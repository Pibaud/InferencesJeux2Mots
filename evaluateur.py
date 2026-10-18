import argparse
import html
import json
import sys
import webbrowser
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import requests

from vecteurs.build_vecteurs import (
    AGENTS_PATHS,
    DATASET_PATH,
    VALID_STATUSES,
    api,
    charger_agents,
    determiner_definitude,
    construire_vecteur_termes,
    inserer_dataset,
    parse_phrase,
    predict,
    predict_relation,
    predict_relation_details,
    term2sig,
)


MODES = ("seuil", "complet", "tous")
RAPPORT_EXPLICATION_PATH = Path(__file__).resolve().parent / "explication_evaluation.html"


def demander_mode() -> str:
    print("\nMode :")
    print("1. seuil (forêt, fusion >= 0.5)")
    print("2. complet (un arbre, sans seuil)")
    print("3. tous")
    choix = input("Choisissez un mode [1] : ").strip() or "1"
    modes = {"1": "seuil", "2": "complet", "3": "tous"}
    if choix not in modes:
        raise ValueError("Mode invalide. Choisissez 1, 2 ou 3.")
    return modes[choix]


def executer_interactivement() -> int:
    print("Évaluateur d'arbres symboliques")
    print("1. Régénérer les arbres")
    print("2. Évaluer une expression")
    print("3. Évaluer un dataset de test")
    print("4. Évaluer une expression et générer l'arbre explicatif HTML")
    action = input("Choisissez une action [2] : ").strip() or "2"
    if action not in {"1", "2", "3", "4"}:
        raise ValueError("Action invalide. Choisissez 1, 2, 3 ou 4.")

    mode = demander_mode()
    if action == "1":
        chemin = input(
            f"Chemin du dataset d'entraînement [{DATASET_PATH}] : "
        ).strip()
        return regenerer(mode, Path(chemin) if chemin else DATASET_PATH)
    if action == "3":
        chemin = input("Chemin du dataset JSON de test : ").strip()
        if not chemin:
            raise ValueError("Le chemin du dataset ne peut pas être vide.")
        details = input("Afficher le détail des prédictions ? [o/N] : ").strip().lower()
        modes = list(AGENTS_PATHS) if mode == "tous" else [mode]
        for current_mode in modes:
            resultat = evaluer_dataset(
                Path(chemin), current_mode, details in {"o", "oui", "y", "yes"}
            )
            if resultat != 0:
                return resultat
        return 0
    if action == "4":
        expression = input("Expression à expliquer (ex. chaise de fer) : ").strip()
        if not expression:
            raise ValueError("L'expression ne peut pas être vide.")
        sortie = input(f"Fichier HTML [{RAPPORT_EXPLICATION_PATH}] : ").strip()
        ouvrir = input("Ouvrir le rapport dans le navigateur ? [O/n] : ").strip().lower()
        return evaluer_avec_explication_html(
            expression,
            mode,
            Path(sortie) if sortie else RAPPORT_EXPLICATION_PATH,
            ouvrir not in {"n", "non", "no"},
        )

    expression = input("Expression à évaluer (ex. chaise de fer) : ").strip()
    if not expression:
        raise ValueError("L'expression ne peut pas être vide.")
    return evaluer(expression, mode)


def regenerer(mode: str, dataset_path: Path = DATASET_PATH) -> int:
    modes = list(AGENTS_PATHS) if mode == "tous" else [mode]
    print(f"Dataset d'entraînement : {dataset_path}")
    for current_mode in modes:
        print(f"\n=== Régénération du mode {current_mode} ===", flush=True)
        model = inserer_dataset(current_mode, dataset_path)
        relation_count = len(model["agents"])
        agent_count = sum(
            bool(trees)
            for definitudes in model["agents"].values()
            for trees in definitudes.values()
        )
        print(f"Arbres sauvegardés dans {AGENTS_PATHS[current_mode]}")
        print(f"Relations représentées : {relation_count}")
        print(f"Agents avec arbres (relation × définitude) : {agent_count}")
    return 0


def evaluer(expression: str, mode: str) -> int:
    modes = list(AGENTS_PATHS) if mode == "tous" else [mode]
    for current_mode in modes:
        if len(modes) > 1:
            print(f"\n=== Évaluation en mode {current_mode} ===")
        relation = predict_relation(expression, current_mode)
        print(f"Relation prédite : {relation}")
    return 0


def rendre_noeud_html(node: dict[str, Any]) -> str:
    selected = node["selectionne"]
    best = node["meilleur"]
    css_class = "tree-node selected" if selected else "tree-node best" if best else "tree-node"
    kind = "Généralisation fusionnée" if node["generalisation"] else "Exemple"
    badge = "Chemin retenu" if selected else "Meilleur enfant comparé" if best else "Alternative"
    cohesion = node["cohesion_fusion"]
    cohesion_html = (
        f"<span>Cohésion de fusion : {cohesion:.3f}</span>" if cohesion is not None else ""
    )
    examples_html = "".join(
        f"<li>{html.escape(str(example))}</li>"
        for example in node["exemples_representatifs"]
    )
    hidden_examples = node["exemples_masques"]
    if hidden_examples:
        examples_html += f"<li class=\"muted\">… et {hidden_examples} autre(s) exemple(s)</li>"
    examples_section = f"<ul class=\"examples\">{examples_html}</ul>" if examples_html else ""
    branches_html = ""
    if node["enfants"]:
        branches_html = "<ul class=\"branches\">" + "".join(
            f"<li>{rendre_noeud_html(child)}</li>" for child in node["enfants"]
        ) + "</ul>"
    return (
        f"<section class=\"{css_class}\">"
        f"<div class=\"node-heading\"><strong>{kind} · {node['exemples']} ex.</strong>"
        f"<span class=\"badge\">{badge}</span></div>"
        f"<div class=\"metrics\"><span>Similarité à l'entrée : "
        f"{node['similarite']:.3f}</span>{cohesion_html}</div>"
        f"<p>{html.escape(str(node['decision']))}</p>{examples_section}</section>"
        f"{branches_html}"
    )


def generer_html_explication(
    expression: str,
    mode: str,
    relation: str,
    similarite_finale: float,
    similarite_racine: float,
    explication: dict[str, Any],
) -> str:
    def rendre_score(label: str, score: float) -> str:
        winner_class = ' class="winner"' if label == relation else ""
        return f"<li{winner_class}>{html.escape(str(label))} : {score:.3f}</li>"

    scores_html = "".join(
        rendre_score(label, score)
        for label, score in sorted(
            explication["agents"].items(), key=lambda item: item[1], reverse=True
        )
    )
    tree_html = rendre_noeud_html(explication["arbre_explicatif"])
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Explication de « {html.escape(expression)} »</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; color: #172033; background: #f3f6fa; }}
body {{ margin: 0; }}
header {{ background: #172033; color: #fff; padding: 24px max(24px, calc((100% - 1100px) / 2)); }}
h1 {{ margin: 0 0 8px; font-size: 1.5rem; }}
header p {{ margin: 0; color: #d0d9e7; }}
main {{ max-width: 1100px; margin: 24px auto; padding: 0 20px 40px; }}
.summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px; }}
.metric, .panel {{ background: #fff; border: 1px solid #dce3ed; border-radius: 10px; padding: 16px; }}
.metric strong {{ display: block; font-size: 1.25rem; margin-top: 5px; }}
.note {{ color: #4b5c72; line-height: 1.55; }}
.scores {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 0; list-style: none; }}
.scores li {{ border: 1px solid #dce3ed; border-radius: 999px; padding: 6px 11px; }}
.scores .winner {{ border-color: #2874c8; background: #eaf3ff; font-weight: 700; }}
.tree {{ list-style: none; padding: 0; }}
.branches {{ list-style: none; margin: 0 0 0 18px; padding: 0 0 0 25px; border-left: 2px solid #ccd6e3; }}
.branches > li {{ position: relative; padding: 12px 0 2px; }}
.branches > li::before {{ content: ""; position: absolute; top: 28px; left: -25px; width: 23px; border-top: 2px solid #ccd6e3; }}
.tree-node {{ background: #fff; border: 1px solid #dce3ed; border-radius: 9px; padding: 12px 14px; }}
.tree-node.selected {{ border: 2px solid #2874c8; background: #f0f7ff; }}
.tree-node.best {{ border-style: dashed; border-color: #d18a16; }}
.node-heading, .metrics {{ display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }}
.badge {{ color: #245b94; font-size: .8rem; font-weight: 700; }}
.best .badge {{ color: #8a5700; }}
.metrics, .muted {{ color: #65758a; font-size: .9rem; }}
.tree-node p {{ margin: 8px 0; }}
.examples {{ margin: 8px 0 0; padding-left: 20px; color: #405169; }}
.legend {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0; color: #526071; font-size: .9rem; }}
@media (max-width: 600px) {{ header {{ padding: 20px; }} main {{ padding: 0 12px 28px; }} .branches {{ margin-left: 4px; padding-left: 16px; }} .branches > li::before {{ left: -16px; width: 14px; }} }}
</style>
</head>
<body>
<header><h1>Pourquoi « {html.escape(expression)} » a été classé « {html.escape(relation)} »</h1>
<p>Mode {html.escape(mode)} · analyse des généralisations de l'arbre appris</p></header>
<main>
<section class="summary">
  <div class="metric">Relation prédite<strong>{html.escape(relation)}</strong></div>
  <div class="metric">Similarité à la racine<strong>{similarite_racine:.3f}</strong></div>
  <div class="metric">Similarité finale<strong>{similarite_finale:.3f}</strong></div>
  <div class="metric">Dimensions de l'entrée<strong>{explication['dimensions_entree']}</strong></div>
</section>
<section class="panel"><h2>Scores des classes candidates</h2><ul class="scores">{scores_html}</ul></section>
<section class="panel"><h2>Chemin de généralisation</h2>
<p class="note">Chaque nœud fusionné généralise plusieurs exemples. Le chemin bleu montre les généralisations retenues : la descente continue lorsque la similarité avec l'entrée ne diminue pas. Les autres enfants sont affichés comme alternatives, avec leurs exemples représentatifs.</p>
<div class="legend"><span>Bleu : chemin suivi</span><span>Orange pointillé : meilleur enfant comparé, non retenu</span></div>
<ul class="tree"><li>{tree_html}</li></ul></section>
</main>
</body></html>'''


def evaluer_avec_explication_html(
    expression: str, mode: str, sortie: Path, ouvrir: bool = True
) -> int:
    modes = list(AGENTS_PATHS) if mode == "tous" else [mode]
    for current_mode in modes:
        relation, root_score, final_score, example, explanation = predict_relation_details(
            expression, current_mode, include_tree_explanation=True
        )
        output_path = sortie
        if len(modes) > 1:
            suffix = output_path.suffix or ".html"
            output_path = output_path.with_name(f"{output_path.stem}_{current_mode}{suffix}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            generer_html_explication(
                expression,
                current_mode,
                relation,
                final_score,
                root_score,
                explanation,
            ),
            encoding="utf-8",
        )
        print(f"Relation prédite ({current_mode}) : {relation} | similarité : {final_score:.3f}")
        if example:
            print(f"Exemple terminal : {example}")
        print(f"Rapport HTML créé : {output_path}")
        if ouvrir:
            webbrowser.open(output_path.resolve().as_uri())
    return 0


def evaluer_dataset(chemin: Path, mode: str, details: bool = False) -> int:
    """Évalue les exemples d'un fichier JSON avec les agents déjà entraînés."""
    dataset = json.loads(chemin.read_text(encoding="utf-8"))
    if not isinstance(dataset, list):
        raise ValueError("Le fichier de test doit contenir une liste JSON d'exemples.")

    if any(AGENTS_PATHS[mode].glob("*.json")):
        model = charger_agents(mode)
    else:
        print(f"Aucun agent trouvé pour le mode {mode} : entraînement du modèle.")
        model = inserer_dataset(mode)

    stats_par_classe: dict[str, dict[str, int]] = defaultdict(
        lambda: {"exemples": 0, "classees": 0, "correctes": 0}
    )
    predictions_par_classe: Counter[str] = Counter()
    nombre_eligible = nombre_classe = nombre_correct = nombre_ignore = nombre_exclu = 0

    for index, exemple in enumerate(dataset, start=1):
        if not isinstance(exemple, dict):
            nombre_ignore += 1
            continue

        statut = exemple.get("statut")
        if statut is not None and statut not in VALID_STATUSES:
            nombre_exclu += 1
            continue

        relation_attendue = exemple.get("relation_humaine")
        mot_a = exemple.get("mot_a")
        mot_b = exemple.get("mot_b")
        if (not isinstance(relation_attendue, str) or not relation_attendue.strip()
                or not isinstance(mot_a, str) or not mot_a.strip()
                or not isinstance(mot_b, str) or not mot_b.strip()):
            texte = exemple.get("texte_complet")
            if isinstance(texte, str) and isinstance(relation_attendue, str) and relation_attendue.strip():
                try:
                    mot_a, mot_b = parse_phrase(texte)
                except ValueError:
                    nombre_ignore += 1
                    continue
            else:
                nombre_ignore += 1
                continue

        relation_attendue = relation_attendue.strip()
        stats = stats_par_classe[relation_attendue]
        stats["exemples"] += 1
        nombre_eligible += 1
        erreur: str | None = None
        relation_predite: str | None = None

        try:
            id_a = api.get_node_id_by_name(mot_a)
            id_b = api.get_node_id_by_name(mot_b)
            if id_a is None or id_b is None:
                erreur = "terme introuvable dans JDM"
            else:
                vecteur = construire_vecteur_termes(id_a, id_b)
                definitude = determiner_definitude(
                    str(exemple.get("texte_complet") or f"{mot_a} de {mot_b}"), mot_b
                )
                relation_predite = predict(model, vecteur, definitude, mode)[0]
        except ValueError as error:
            erreur = str(error)
        except requests.RequestException as error:
            raise RuntimeError(f"Échec de l'appel à l'API JDM pour l'exemple {index}: {error}") from error

        if relation_predite is not None:
            nombre_classe += 1
            stats["classees"] += 1
            predictions_par_classe[relation_predite] += 1
            if relation_predite == relation_attendue:
                nombre_correct += 1
                stats["correctes"] += 1

        if details:
            resultat = relation_predite if relation_predite is not None else f"non classé ({erreur})"
            print(f"[{index}] attendu={relation_attendue} | prédit={resultat}")

    print(f"\n=== Évaluation du dataset : {chemin} | mode {mode} ===")
    print(
        f"Global : {nombre_correct}/{nombre_classe} relations bien classées "
        f"({nombre_correct / nombre_classe:.1%})" if nombre_classe else
        "Global : 0/0 relations bien classées (aucun exemple classé)"
    )
    print(
        f"Exemples évaluables : {nombre_eligible} | classés : {nombre_classe} "
        f"| non classés : {nombre_eligible - nombre_classe} "
        f"| ignorés : {nombre_ignore} | exclus par statut : {nombre_exclu}"
    )
    print("\nStatistiques par classe réelle :")
    for relation, stats in sorted(stats_par_classe.items()):
        denominateur = stats["classees"]
        taux = f"{stats['correctes'] / denominateur:.1%}" if denominateur else "n/a"
        precision_denominateur = predictions_par_classe[relation]
        precision = (
            f"{stats['correctes'] / precision_denominateur:.1%}"
            if precision_denominateur else "n/a"
        )
        non_classees = stats["exemples"] - stats["classees"]
        print(
            f"  {relation}: {stats['correctes']}/{denominateur} bien classées "
            f"({taux}), {non_classees} non classée(s), "
            f"précision des prédictions de cette classe : "
            f"{stats['correctes']}/{precision_denominateur} ({precision})"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Régénère les arbres ou évalue une expression.")
    parser.add_argument(
        "expression",
        nargs="?",
        help="Expression à évaluer, par exemple: 'chaise de fer'.",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Régénère les arbres au lieu d'évaluer une expression.",
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        help="seuil: forêt; complet: arbre unique; tous: les deux.",
    )
    args = parser.parse_args()

    try:
        if not args.expression and not args.train and not args.mode:
            return executer_interactivement()
        mode = args.mode or "seuil"
        if args.train:
            return regenerer(mode)
        if not args.expression:
            parser.error("une expression est nécessaire sans --train")
        return evaluer(args.expression, mode)
    except (EOFError, OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())