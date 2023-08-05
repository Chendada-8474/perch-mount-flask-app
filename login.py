from query_mysql import get_users_login_info
from flask_login import UserMixin, LoginManager


login_manager = LoginManager()
login_manager.login_view = "login"


class User(UserMixin):
    def is_admin(self):
        return self.admin

    def is_super_admin(self):
        return self.super_admin


@login_manager.user_loader
def user_loader(user_name):
    users = get_users_login_info()
    if user_name not in users:
        return

    user = User()
    user.id = user_name
    user.member_id = users[user_name]["member_id"]
    user.admin = users[user_name]["admin"]
    user.super_admin = users[user_name]["super_admin"]
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get("user_name")
    users = get_users_login_info()
    if email not in users:
        return

    user = User()
    user.id = email
    return user
