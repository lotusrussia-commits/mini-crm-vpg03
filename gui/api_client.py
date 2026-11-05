import requests


API_URL = "http://127.0.0.1:8000"


class APIClient:
    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    def _get(self, path, params=None):
        response = requests.get(
            f"{self.base_url}{path}",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _send(self, method, path, json=None):
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            json=json,
            timeout=10,
        )
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return True
        return response.json()

    def get_clients(self, q=None, status=None, include_archived=False):
        params = {}
        if q:
            params["q"] = q
        if status:
            params["status"] = status
        if include_archived:
            params["include_archived"] = "true"
        return self._get("/clients/", params)

    def get_client(self, client_id):
        return self._get(f"/clients/{client_id}")

    def create_client(self, client_data):
        return self._send("POST", "/clients/", client_data)

    def update_client(self, client_id, client_data):
        return self._send("PUT", f"/clients/{client_id}", client_data)

    def archive_client(self, client_id):
        return self._send("DELETE", f"/clients/{client_id}")

    def restore_client(self, client_id):
        return self._send("POST", f"/clients/{client_id}/restore")

    def delete_client(self, client_id):
        return self.archive_client(client_id)

    def get_deals(self, q=None, status=None, client_id=None):
        params = {}
        if q:
            params["q"] = q
        if status:
            params["status"] = status
        if client_id is not None:
            params["client_id"] = client_id
        return self._get("/deals/", params)

    def get_deal(self, deal_id):
        return self._get(f"/deals/{deal_id}")

    def create_deal(self, deal_data):
        return self._send("POST", "/deals/", deal_data)

    def update_deal(self, deal_id, deal_data):
        return self._send("PUT", f"/deals/{deal_id}", deal_data)

    def delete_deal(self, deal_id):
        return self._send("DELETE", f"/deals/{deal_id}")

    def get_tasks(self, q=None, status=None, client_id=None, deal_id=None):
        params = {}
        if q:
            params["q"] = q
        if status:
            params["status"] = status
        if client_id is not None:
            params["client_id"] = client_id
        if deal_id is not None:
            params["deal_id"] = deal_id
        return self._get("/tasks/", params)

    def get_task(self, task_id):
        return self._get(f"/tasks/{task_id}")

    def create_task(self, task_data):
        return self._send("POST", "/tasks/", task_data)

    def update_task(self, task_id, task_data):
        return self._send("PUT", f"/tasks/{task_id}", task_data)

    def delete_task(self, task_id):
        return self._send("DELETE", f"/tasks/{task_id}")
