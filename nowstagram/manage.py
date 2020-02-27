from flask_script import Manager
from nowstagram import app,db
from nowstagram.models import User,Image,Comment
import random,unittest
from sqlalchemy import or_,and_


manager=Manager(app=app)


def  get_image_url():
   return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


@manager.command

#insert
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0,100):
        db.session.add(User('User'+str(i+1),'a'+str(i)))
        for j in range(0,3):
            db.session.add(Image(get_image_url(),i+1))
            for k in range(0,3):
               db.session.add(Comment("this is a comment "+str(k+1),1+3*i+j,i+1))

    db.session.commit()
   # update
    User.query.filter_by(id = 50).update({'username':'新名字'+str(i)})
    db.session.commit()


#query
    print("1",User.query.all())
    print("2",User.query.get(3))
    print("3",User.query.filter_by(id=5).first())
    print("4",User.query.order_by(User.id.desc()).offset(1).limit(2).all())
    print("5",User.query.filter(User.username.endswith('0')).limit(3).all())
    print("6",User.query.filter(or_(User.id==88,User.id==99)).all())
    print("7",User.query.filter(and_(User.id>85,User.id<93)).first_or_404())

#page
    print("9",User.query.order_by(User.id.desc()).paginate(page=1,per_page=10).items)

# 1:N
    user=User.query.get(1)
    print("10",user.images)

#backref
    image=Image.query.get(5)
    print("11",image.user)

#delete
    # for i in range(99, 100):
    #     comment = Comment.query.get(i + 1)
    #     db.session.delete(comment)

    images = Image.query.order_by(Image.id.desc()).limit(10).all()
    print("12",images)


@manager.command
def run_test():
    tests=unittest.TestLoader().discover('/')
    pass


if __name__=='__main__':
    manager.run()