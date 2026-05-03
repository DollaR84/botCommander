from typing import Optional

from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import check_password_hash

from config import AdminConfig


class AdminUser(UserMixin):

    def __init__(self, username: str):
        self.id = "admin"
        self.username = username


class AuthManager:

    def __init__(self, config: AdminConfig):
        self.config = config

        self.login_manager = LoginManager()

    def init_app(self, app: Flask) -> None:
        app.config["SECRET_KEY"] = self.config.secret_key
        self.login_manager.init_app(app)

        self.login_manager.login_view = "auth.login"
        self.login_manager.user_loader(self._load_user)

    def _load_user(self, user_id: str) -> Optional[AdminUser]:
        if user_id == "admin":
            return AdminUser(self.config.username)
        return None

    def login(self, username: str, password: str) -> bool:
        is_valid_user = username == self.config.username
        is_valid_password = check_password_hash(self.config.password_hash, password)

        if is_valid_user and is_valid_password:
            user = AdminUser(username)
            return bool(login_user(user))
        return False

    def logout(self) -> bool:
        return bool(logout_user())
