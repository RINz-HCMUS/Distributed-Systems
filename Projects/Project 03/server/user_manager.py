import json
import os

class UserManager:
    def __init__(self):
        # Lấy root của project (…/Project 03)
        root_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        # Thư mục data/
        data_dir = os.path.join(root_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        self.path = os.path.join(data_dir, "users.json")
        self.users = {}
        self._load()

    # -------------------------------------------------
    # INTERNAL IO
    # -------------------------------------------------

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.users = json.load(f)
        else:
            self._save()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=2)

    # -------------------------------------------------
    # AUTH
    # -------------------------------------------------

    def validate(self, username, password):
        if username not in self.users:
            return False, "user_not_found"

        if self.users[username]["password"] != password:
            return False, "wrong_password"

        return True, "success"

    def create_user(self, username, password):
        if username in self.users:
            return False, "user_exists"

        self.users[username] = {
            "password": password,
            "score": 0
        }
        self._save()
        return True, "success"

    # -------------------------------------------------
    # SCORE
    # -------------------------------------------------

    def add_score(self, username, delta):
        if username in self.users:
            self.users[username]["score"] += delta
            self._save()

    def get_total_score(self, username):
        return self.users.get(username, {}).get("score", 0)

    # -------------------------------------------------
    # RANKING
    # -------------------------------------------------

    def get_ranking(self, top_n=25):
        sorted_users = sorted(
            self.users.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        top = []
        for i, (u, info) in enumerate(sorted_users[:top_n], start=1):
            top.append({
                "rank": i,
                "username": u,
                "score": info["score"]
            })

        return top, sorted_users
