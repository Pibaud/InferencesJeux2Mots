import sqlite3
import json
import os

DB_PATH = os.environ.get("DB_PATH", "annotations.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texte_complet TEXT UNIQUE,
                mot_a TEXT,
                mot_b TEXT,
                relation_ia TEXT,
                relation_humaine TEXT,
                statut TEXT DEFAULT 'a_verifier', -- 'a_verifier', 'valide', 'corrige', 'a_revoir', 'supprime'
                date_annotation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def importer_depuis_json(json_path):
    init_db()
    if not os.path.exists(json_path):
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    inseres = 0
    with get_conn() as conn:
        for item in items:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO annotations 
                (texte_complet, mot_a, mot_b, relation_ia, relation_humaine)
                VALUES (?, ?, ?, ?, ?)
                """,
                (item["texte_complet"], item["A"], item["B"], item["relation"], item["relation"])
            )
            inseres += cur.rowcount
        conn.commit()
    return inseres

def get_prochain_syntagme(statut_cible='a_verifier'):
    with get_conn() as conn:
        row = conn.execute("""
            WITH ClassCounts AS (
                -- 1. On calcule la répartition actuelle des classes validées
                SELECT relation_humaine AS relation, COUNT(*) AS compte
                FROM annotations
                WHERE statut IN ('valide', 'corrige')
                GROUP BY relation_humaine
            )
            SELECT a.*
            FROM annotations a
            -- 2. On associe chaque syntagme en attente à la popularité de sa pré-annotation IA
            LEFT JOIN ClassCounts c ON a.relation_ia = c.relation
            WHERE a.statut = ?
            -- 3. On trie par classe la moins représentée, puis au hasard pour éviter les conflits
            ORDER BY COALESCE(c.compte, 0) ASC, RANDOM()
            LIMIT 1
        """, (statut_cible,)).fetchone()
        return dict(row) if row else None

def get_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM annotations").fetchone()[0]
        # Les "faits" incluent tout ce qui n'est plus dans la boucle de vérification initiale ou de révision
        faits = conn.execute("SELECT COUNT(*) FROM annotations WHERE statut IN ('valide', 'corrige', 'supprime')").fetchone()[0]
        # On compte spécifiquement ceux mis de côté
        a_revoir = conn.execute("SELECT COUNT(*) FROM annotations WHERE statut = 'a_revoir'").fetchone()[0]
        return faits, total, a_revoir

def maj_annotation(syntagme_id, relation_choisie, statut):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE annotations 
            SET relation_humaine = ?, statut = ?, date_annotation = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (relation_choisie, statut, syntagme_id)
        )
        conn.commit()

def exporter_gold_json():
    with get_conn() as conn:
        # On n'exporte QUE les annotations validées par l'humain
        rows = conn.execute(
            "SELECT texte_complet, mot_a, mot_b, relation_humaine, statut FROM annotations WHERE statut IN ('valide', 'corrige')"
        ).fetchall()
        return [dict(r) for r in rows]
    
def get_distribution_classes():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT relation_humaine AS relation, COUNT(*) AS compte
            FROM annotations
            WHERE statut IN ('valide', 'corrige')
            GROUP BY relation_humaine
            ORDER BY compte DESC
        """).fetchall()
        return [{"relation": r["relation"], "compte": r["compte"]} for r in rows]
    
def maj_annotation(syntagme_id, relation_choisie, nouveau_statut, statut_attendu):
    with get_conn() as conn:
        # On ajoute "AND statut = ?" pour s'assurer que personne ne l'a modifié entre temps
        cur = conn.execute(
            """
            UPDATE annotations 
            SET relation_humaine = ?, statut = ?, date_annotation = CURRENT_TIMESTAMP
            WHERE id = ? AND statut = ?
            """,
            (relation_choisie, nouveau_statut, syntagme_id, statut_attendu)
        )
        conn.commit()
        # Si rowcount est 0, c'est que le statut avait déjà changé
        return cur.rowcount > 0