import requests

class JDM_API:
    def __init__(self):
        self.base_url = "https://jdm-api.demo.lirmm.fr/v0"

    def get_node_by_name(self, node_name):
        url = f"{self.base_url}/node_by_name/{node_name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


    def get_relations_from_to(self,node1_name,node2_name):
        url = f"{self.base_url}/relations/from/{node1_name}/to/{node2_name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_relations_from_to_by_id(self, node1_id, node2_id, **kwargs):
        url = f"{self.base_url}/relations/from_by_id/{node1_id}/to_by_id/{node2_id}"
        
        response = requests.get(url, params=kwargs)
        response.raise_for_status()
        return response.json()