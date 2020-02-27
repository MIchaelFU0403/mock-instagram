from nowstagram import db, login_manager
import random
from _datetime import datetime

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # class 小写
    status = db.Column(db.Integer,default=0)
    user = db.relationship('User')

    def __init__(self, content,image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id


    def __repr__(self):
        return '<Comment %d %s>' %(self.id, self.content)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(280))
    head_url = db.Column(db.String(256))
    images = db.relationship('Image', backref='user')
    salt = db.Column(db.String(32)) #密码加密


    def __init__ (self, username, password,salt='') :
        self.username = username
        self.password = password
        self.salt=salt
        self.head_url = 'http://images.nowcoder.com/head/'+str(random.randint(0, 1000)) + 'm.png'

    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)


# class that you use to represent users needs
# to implement these properties and methods:
# 认为只要是登录的用户，都是激活的，真的，非匿名的

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return (self.id)
    #问题出现在源码中，get_id()方法返回的是unicode(self.id)，
    # 但是python3取消了unicode方法！所以必须重写该方法
    # ，重写后就可以使用@login_required对路由进行保护了了！



# 通过traceback id，找到详细信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)




class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(580))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.create_date = datetime.now()

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


