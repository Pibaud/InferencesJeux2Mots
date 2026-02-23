from model.api import JDM_API

class VM:
    def __init__(self):
        self.jdm_api = JDM_API()

    def fetch_node_id_by_name(self, node_name):
        """
        retourne l'id d'un node par son nom
        """
        return self.jdm_api.get_node_by_name(node_name).get("id")

    def fetch_relation_by_id(self, node_id, node_id2):
        """
        retourne les relations entre deux nodes à partir de leur id
        """
        res =  self.jdm_api.get_relations_from_to_by_id(node_id, node_id2)
        resultat = []
        if res:
            for elem in res["relations"] :
                resultat.append(elem["id"])
            return resultat
        else:
            print("Aucune relation trouvée entre les deux nœuds.")
            return None
        
    def fetch_refinements_by_name(self, node_name):
        """
        retourne les raffinements d'un node à partir de son nom
        """
        res = self.jdm_api.get_refinements(node_name)
        resultat = []
        if res:
            for elem in res["refinements"] :
                resultat.append(elem["id"])
            return resultat
        else:
            print("Aucun raffinement trouvé pour ce nœud.")
            return None
        
    def fetch_node_by_name(self, node_name):
        """
        retourne les informations d'un node à partir de son nom
        """
        return self.jdm_api.get_node_by_name(node_name)
    
    def fetch_relations_from(self, node_name):
        """
        retourne les relations à partir d'un node
        """
        return self.jdm_api.get_relations_from(node_name)

    def fetch_relation_name_by_type_id(self, type_id):
        """
        Retourne le nom (gpname) d'une relation à partir de son id
        """
        relations = self.jdm_api.get_relation_types()
        for relation in relations:
            if relation["id"] == type_id:
                return relation["name"]