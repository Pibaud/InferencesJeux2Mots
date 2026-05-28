import requests
import hashlib
import os
import json

class JDM_API:
    def __init__(self):
        self.base_url = "https://jdm-api.demo.lirmm.fr/v0"
     
        self.session = requests.Session()

    def get_node_id_by_name(self, node_name):
        url = f"{self.base_url}/node_by_name/{node_name}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        
        dossier = "cache/nodeByName/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = self.session.get(url)
        response.raise_for_status()
        data =  response.json().get('id')
    
        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    
    def get_node_by_id(self, node_id):
        url = f"{self.base_url}/node_by_id/{node_id}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/nodeById/"
        path_complet = os.path.join(dossier, (md5String + ".json"))
        
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        
        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return data

    def get_relations_from_to_by_id(self, node1_id, node2_id, **kwargs):
        url = f"{self.base_url}/relations/from_by_id/{node1_id}/to_by_id/{node2_id}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/relationFromTo/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data

        response = self.session.get(url, params=kwargs)
        response.raise_for_status()
        data = response.json()
        
        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    def get_refinements(self, node_name):
        url = f"{self.base_url}/refinements/{node_name}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/refinements/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            try:
                with open(path_complet, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            except (json.JSONDecodeError, OSError):
                pass

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code >= 500:
                return {"nodes": []}
            raise
        except (requests.RequestException, ValueError):
            return {"nodes": []}

        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    def get_relations_from_by_id(self, node_id, types_ids=None,min_weight=None,limit=300):
        url = f"{self.base_url}/relations/from_by_id/{node_id}"
        query = {}
        if types_ids is not None:
            query["types_ids"] = types_ids
        if min_weight is not None:
            query["min_weight"] = min_weight
        query["limit"] = limit

        cache_key = f"{url}|types_ids={types_ids}&min_weight={min_weight}&limit={limit}"
        md5String = hashlib.md5(cache_key.encode()).hexdigest()

        if types_ids is None:
            dossier = "cache/relationsFromById/"
        else:
            dossier = "cache/relationsFromById/" + str(types_ids) + "/"

        path_complet = os.path.join(dossier, (md5String + ".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data

        response = self.session.get(url, params=query)
        response.raise_for_status()
        data = response.json()

        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    def get_relation_types(self):
        """
        Récupère tous les types de relations (rtid, name, nom_etendu, info)
        """
        url = f"{self.base_url}/relations_types"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/relationTypes/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = self.session.get(url)
        response.raise_for_status()
        data= response.json()

        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    
    def get_relation_name_by_type_id(self, type_id):
        relation_types = self.get_relation_types()
        for rt in relation_types:
            if rt["id"] == type_id:
                return rt["name"]
        return None
    
    def get_relations_from(self, node_name):
        url = f"{self.base_url}/relations/from/{node_name}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/relationsFromByName/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = self.session.get(url)
        response.raise_for_status()
        data =  response.json()

        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data
    
    def get_relations_from_to(self, node_name1, node_name2):
        url = f"{self.base_url}/relations/from/{node_name1}/to/{node_name2}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/relationsFromToByName/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = self.session.get(url)
        response.raise_for_status()
        data =  response.json()

        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data
    
    def get_top_synonyms(self, node_id, limit=4):

        data = self.get_relations_from_by_id(node_id, types_ids=5)
        
        if not data or "relations" not in data:
            return []

        nodes_lookup = {n['id']: n['name'] for n in data.get('nodes', [])}

        syn_relations = [r for r in data["relations"] if r["w"] > 0]
        sorted_syns = sorted(syn_relations, key=lambda x: x["w"], reverse=True)

        top_synonyms = []
        for rel in sorted_syns[:limit]:
            syn_id = rel["node2"]
            top_synonyms.append({
                "id": syn_id,
                "name": nodes_lookup.get(syn_id, "Inconnu"),
                "w": rel["w"]
            })

        return top_synonyms