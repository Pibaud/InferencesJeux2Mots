import json
import sys
from api.api import JDM_API

jdm_api = JDM_API()

def fetch_node(node_name):
    node = jdm_api.get_node_by_name(node_name)
        
    print(f"\n--- Résultats pour : {node_name} ---")
    print(json.dumps(node, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = input("Entrez le nom du nœud à rechercher : ")
    
    fetch_node(name)