from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
app = Flask( __name__)
#break jiejia 拓展

app.config.from_pyfile('app.conf')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')#break jiejia 拓展

app.secret_key='rgfadfasdfew' #flash消息，用Session,需要密钥

db = SQLAlchemy(app=app)

login_manager = LoginManager(app)  #引入flask——login扩展
login_manager.login_view='/regloginpage/' # unauthorized page
login_manager.init_app(app)
# flask_login 核心函数和属性
# login_user(user)
# logout_user()
# login_required
# current_user

# User用户接口
# is_authenticated
# is_active
# is_anonymous
# get_id()

from nowstagram import views,models

