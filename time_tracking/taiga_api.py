import requests

class TaigaManager:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        url = f"{self.base_url}/auth"
        data = {
            "type": "normal",
            "username": username,
            "password": password
        }
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json()['auth_token']
            self.session.headers.update({'Authorization': 'Bearer ' + self.token})

    def get_project_by_slug(self, slug):
        url = f"{self.base_url}/projects/by_slug?slug={slug}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_sprints_for_project(self, project_id):
        url = f"{self.base_url}/milestones?project={project_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    def get_sprint_by_name(self, project_id, sprint_name):
        url = f"{self.base_url}/milestones?project={project_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            sprints = response.json()
            for sprint in sprints:
                if sprint['name'] == sprint_name:
                    return sprint
        return None

    def get_user_stories_for_sprint(self, sprint_id):
        url = f"{self.base_url}/userstories?milestone={sprint_id}"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else None

    def get_tasks_for_story(self, user_story_id):
        url = f"{self.base_url}/tasks?user_story={user_story_id}"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else None


    def get_task_status(self, status_id):
        url = f"{self.base_url}/task-statuses/{status_id}"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else None

    def get_custom_attributes_for_task(self, task_id):
        url = f"{self.base_url}/tasks/custom-attributes-values/{task_id}"
        response = self.session.get(url)
        response.raise_for_status()
        task_data = response.json()
        spent_time = task_data.get('attributes_values', {}).get('2')
        return spent_time if spent_time else "00:00"

    def get_user(self, user_id):
        url = f"{self.base_url}/users/{user_id}"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else None

    def get_user_story_status(self, status_id):
        url = f"{self.base_url}/userstory-statuses/{status_id}"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else None

    def get_user_stories_for_project(self, project_id):
        url = f"{self.base_url}{project_id}"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else None