# mock-instagram
a small picture-sharing website based on python flask +sqlite+Ajax+ qiniuSDK

this program is small because only achieving some core functions like 1.register 2.login 3.browse other's pages 3.upload your own page 4.comment anyone's photographs


# package using:
flask
flask-login 0.3.1
flask-sqlalchemy
flask-script
qiniu

# the structure of this project
manage.py  \\ 1. to init the database  2.to start the unit testing   3.runserver and debug

runserver.py  \\to runserver

test.py  \\ about unit testing

nowstagram->

app.config   \\1.to connect the database  sqlite  (url , track)  2.info about qiniu SDK （access key，secret key, bucketname, domain name）

models.py   \\ caputure the models to use ORM

qiniusdk.py  \\upload the files to my site to store the photographs

veiws.py  \\support the main functions (Business Logic Layer)

init.py  \\1. create app, manager,db.   2.set secretkey   3.use extension of jinjia to use 'break' in flask
4.create login_manager and the login_view page.

models.py   \\ caputure the models to use ORM

static   \\ javascript css images font

templates  \\ html pages   
