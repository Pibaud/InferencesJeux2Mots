import streamlit as st
import pandas as pd
import db
import json

st.set_page_config(page_title="JDM Annotateur", page_icon="🏷️", layout="centered")
db.init_db()

AIDE_RELATIONS = {
    "r_has_causatif": "A est causé par B (ex: dégâts de la tempête)",
    "r_has_property-1": "A est une propriété de B (ex: sournoiserie du politicien)",
    "r_objet>matiere": "A est composé de B (ex: cuillère de bois, trône de fer)",
    "r_lieu>origine": "A est originaire de B (ex: vin de France, café du Brésil)",
    "r_topic": "A a pour thème B (ex: restaurant de sushis, film d'horreur)",
    "r_depict": "A est une représentation de B (ex: peinture d'un paysage)",
    "r_holo": "A fait partie de B (ex: coque du bateau, écaille du poisson)",
    "r_lieu": "A peut avoir pour lieu B (ex: tour de Pise, sahara d'Algérie)",
    "r_processus_agent": "A est l'action dont l'acteur est B (ex: travail de l'ouvrier)",
    "r_processus_patient": "A est l'action subie par B (ex: travail du bois, ouverture de la porte)",
    "r_processus>instr-1": "A est l'instrument de l'action (ex: clé d'ouverture, clé de la porte)",
    "r_own-1": "A est possédé par B (ex: fusil du soldat, vélo du cycliste)",
    "r_quantificateur": "A sert de mesure à B (ex: brin d'herbe, minute d'attente)",
    "r_social_tie": "A a un rôle social vis-à-vis de B (ex: avocat d'une femme)",
    "r_product_of": "A est produit par B (ex: portrait de Van Gogh, gâteau du pâtissier)",
    "inconnu": "Si aucune de ces relations ne s'applique clairement."
}

RELATIONS_JDM = list(AIDE_RELATIONS.keys())

faits, total, a_revoir = db.get_stats()
progress = faits / total if total > 0 else 0.0

# === MENU LATÉRAL ===
with st.sidebar:
    st.header("⚙️ Options")
    
    # Sélecteur de mode de travail
    mode = st.radio(
        "Mode de travail :",
        options=["Flux normal (nouveaux)", f"Révision ({a_revoir} en attente)"],
        index=0
    )
    
    statut_cible = 'a_verifier' if "Flux normal" in mode else 'a_revoir'
    
    st.divider()
    
    gold_data = db.exporter_gold_json()
    st.download_button(
        label=f"📥 Exporter le dataset Gold ({len(gold_data)})",
        data=json.dumps(gold_data, ensure_ascii=False, indent=4),
        file_name="4_dataset_gold_final.json",
        mime="application/json",
        use_container_width=True,
        help="Exporte uniquement les syntagmes validés ou corrigés."
    )
    
    st.divider()
    st.subheader("ℹ️ Aide : Relations JDM")
    for rel, desc in AIDE_RELATIONS.items():
        st.markdown(f"**{rel}** : {desc}")

# === INTERFACE PRINCIPALE ===
st.progress(progress, text=f"Progression globale : {faits}/{total} traités (Validés ou Supprimés)")

item = db.get_prochain_syntagme(statut_cible)

if not item:
    if statut_cible == 'a_verifier':
        st.success("🎉 Tous les nouveaux syntagmes ont été traités !")
        if a_revoir > 0:
            st.info(f"👉 Il vous reste {a_revoir} syntagmes mis de côté. Passez en mode 'Révision' dans le menu.")
    else:
        st.success("🎉 Tous les syntagmes difficiles ont été révisés !")
else:
    st.markdown(f"### « {item['texte_complet']} »")
    st.caption(f"**A :** {item['mot_a']}  |  **B :** {item['mot_b']}")

    rel_actuelle = item['relation_humaine'] if item['relation_humaine'] != "inconnu" else item['relation_ia']
    idx_ia = RELATIONS_JDM.index(rel_actuelle) if rel_actuelle in RELATIONS_JDM else len(RELATIONS_JDM) - 1

    choix = st.selectbox("Relation :", RELATIONS_JDM, index=idx_ia)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Valider", use_container_width=True, type="primary"):
            db.maj_annotation(item["id"], choix, "valide" if choix == item["relation_ia"] else "corrige")
            st.rerun()

    with col2:
        if st.button("⏳ Plus tard", use_container_width=True):
            db.maj_annotation(item["id"], "inconnu", "a_revoir")
            st.rerun()

    with col3:
        if st.button("🗑️ Supprimer", use_container_width=True):
            db.maj_annotation(item["id"], "inconnu", "supprime")
            st.rerun()

# === STATISTIQUES (S'affichent en bas) ===
st.divider()
st.subheader("📊 Représentativité des classes")

distribution = db.get_distribution_classes()

if distribution:
    df_dist = pd.DataFrame(distribution)
    max_val = int(df_dist["compte"].max())
    
    st.dataframe(
        df_dist,
        column_config={
            "relation": st.column_config.TextColumn("Relation"),
            "compte": st.column_config.ProgressColumn(
                "Volume",
                help="Nombre de syntagmes validés ou corrigés",
                format="%d",
                min_value=0,
                max_value=max_val,
            ),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("Aucune donnée validée pour le moment.")