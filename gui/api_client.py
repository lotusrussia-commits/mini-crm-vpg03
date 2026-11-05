
import requests


API_URL = "http://127.0.0.1:8000"


class APIClient:
    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    # КЛИЕНТЫ

    def get_clients(self):
        response = requests.get(f"{self.base_url}/clients/", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_client(self, client_id):
        response = requests.get(
            f"{self.base_url}/clients/{client_id}", timeout=10
        )
        response.raise_for_status()
        return response.json()

    def create_client(self, client_data):
        response = requests.post(
            f"{self.base_url}/clients/",
            json=client_data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def update_client(self, client_id, client_data):
        response = requests.put(
            f"{self.base_url}/clients/{client_id}",
            json=client_data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete_client(self, client_id):
        response = requests.delete(
            f"{self.base_url}/clients/{client_id}", timeout=10
        )
        response.raise_for_status()
        return True

    # СДЕЛКИ

    def get_deals(self):
        response = requests.get(f"{self.base_url}/deals/", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_deal(self, deal_id):
        response = requests.get(
            f"{self.base_url}/deals/{deal_id}", timeout=10
        )
        response.raise_for_status()
        return response.json()

    def create_deal(self, deal_data):
        response = requests.post(
            f"{self.base_url}/deals/",
            json=deal_data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def update_deal(self, deal_id, deal_data):
        response = requests.put(
            f"{self.base_url}/deals/{deal_id}",
            json=deal_data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete_deal(self, deal_id):
        response = requests.delete(
            f"{self.base_url}/deals/{deal_id}", timeout=10
        )
        response.raise_for_status()
        return True

    # ЗАДАЧИ

    def get_tasks(self):
        response = requests.get(f"{self.base_url}/tasks/", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id):
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}", timeout=10
        )
        response.raise_for_status()
        return response.json()

    def create_task(self, task_data):
        response = requests.post(
            f"{self.base_url}/tasks/",
            json=task_data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def update_task(self, task_id, task_data):
        response = requests.put(
            f"{self.base_url}/tasks/{task_id}",
            json=task_data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete_task(self, task_id):
        response = requests.delete(
            f"{self.base_url}/tasks/{task_id}", timeout=10
        )
        response.raise_for_status()
        return True
