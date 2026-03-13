import requests
import hashlib
import os
import json

class JDM_API:
    def __init__(self):
        self.base_url = "https://jdm-api.demo.lirmm.fr/v0"

    def get_node_id_by_name(self, node_name):
        url = f"{self.base_url}/node_by_name/{node_name}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        #Verif en local pour le cache
        
        dossier = "cache/nodeByName/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = requests.get(url)
        response.raise_for_status()
        data =  response.json().get('id')
        os.makedirs(dossier, exist_ok=True) 
    
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

        response = requests.get(url, params=kwargs)
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
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        response = requests.get(url)
        response.raise_for_status()
        
        data =  response.json()
        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    def get_relations_from_by_id(self, node_id):
        url = f"{self.base_url}/relations/from_by_id/{node_id}"
        md5String = hashlib.md5(url.encode()).hexdigest()
        dossier = "cache/relationsFrom/"
        path_complet = os.path.join(dossier,(md5String+".json"))
        if os.path.isfile(path_complet):
            with open(path_complet, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        response = requests.get(url)
        response.raise_for_status()
        data =  response.json()

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
        
        response = requests.get(url)
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
        
        response = requests.get(url)
        response.raise_for_status()
        data =  response.json()

        os.makedirs(dossier, exist_ok=True)
        with open(path_complet, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data