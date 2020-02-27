from nowstagram import app,db
from flask import render_template,redirect,request,flash,get_flashed_messages,send_from_directory
from nowstagram.models import Image,User,Comment
import random,hashlib,json,uuid,os
from flask_login import login_user, logout_user, current_user, login_required
from nowstagram.qiniusdk import qiniu_upload_file

@app.route('/')  #首页根目录
def index():
    # images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    # images = Image.query.order_by('-id').limit(10).all()
    # images =Image.query.order_by('id desc ').limit(10).all()
    images =Image.query.order_by( Image.id.desc()).limit(10).all()

    # print(current_user.id)

    return render_template('index.html',images=images)

@app.route('/image/<int:image_id>/')  #图片页
@login_required
def image(image_id):
    image =Image.query.get(image_id)
    if image==None:
        return redirect('/')

    # print(current_user.id)


    return render_template('pageDetail.html',image=image)

@app.route('/profile/<int:user_id>/')  #个人主页
@login_required
#需先登录才能访问 ， 可在设置py文件下设置，unauthorized页面
#Views that require your users to be logged in can be
# decorated with the login_required decorator:
def profile(user_id):

    # print(current_user.id)

    user =User.query.get(user_id)
    if user==None:
        return redirect('/')
    paginate=Image.query.filter_by(user_id=user_id).paginate(page=1,per_page=3, error_out=False)#没有的话，标注报错
    return render_template('profile.html',user=user,images=paginate.items,has_next=paginate.has_next)#paginate.has_next判断是否含有下一页

#接口 不刷新页面ajax请求
@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id,page,per_page):
    paginate=Image.query.filter_by(user_id=user_id).paginate(page=page,per_page=per_page, error_out=False)#没有的话，标注报错
    map={'has_next':paginate.has_next}  #用map hasnext标签记录有没有数据
    images=[]
    for image in paginate.items:
        imgvo={'id':image.id,'url':image.url,'comment_count':len(image.comments)}
        images.append(imgvo)

    map['images']=images
    return json.dumps(map)



# {"has_next": false, "images": [{"id": 304, "url": "http://images.nowcoder.com/head/644m.png", "comment_count": 0}, {"id": 305, "url": "http://images.nowcoder.com/head/791m.png", "comment_count": 0}]}




# flash消息方法函数
def redirect_with_msg(target,msg,category): #targetpage
    if msg != None:
        flash(msg,category=category)
    return redirect(target)

@app.route('/regloginpage/') #登录注册页面
def regloginpage():
    msg=''
    #获取flash消息的时候不需要进行category，但要过滤，只筛选出登录注册有关的种类

    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m
    return render_template('login.html',msg=msg,next=request.values.get('next'))



@app.route('/reg/',methods={'GET','POST'})
def reg():
    #request.args html中参数
    #request.form 表单中参数
    #request.value自主选择

    # print(type(request.values.get('username')))
    username=request.values.get('username').strip()

    password=request.values.get('password').strip()
    user = User.query.filter_by(username=username).first()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/',u'用户名或密码未填写','reglogin')

    # if user != None:
    #     flash(u'用户名已存在',category='reglogin')#category表示信息来自哪里
    #     return redirect('/regloginpage/')  调用flash消息方法函数
    if user != None:
        return redirect_with_msg('/regloginpage/',u'用户名已存在','reglogin')


    #password加密
    salt = ''.join(random.sample('0123456789abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 10))
    #随机出10个字符，与点连起来
    a = hashlib.md5()
    #TypeError: Unicode-objects must be encoded before hashing
    a.update((password+salt).encode("utf-8")) #python3中字符对象是unicode对象，不能直接加密，要转成utf-8
    password = a.hexdigest()#md5加密出16进制字符串

    user=User(username,password,salt)
    db.session.add(user)
    db.session.commit()
    # 自动登录
    login_user(user,remember=True) #修改源码 675行is_active  756行is_authenticated:
    # 最后改进方法 重下flask-login 0.3.2
    return redirect('/')



@app.route('/login/',methods={'GET','POST'})
def login():
    # print(type(request.values.get('username')))
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码未填写', 'reglogin')
    #验证用户
    user = User.query.filter_by(username=username).first()
    if user ==None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在', 'reglogin')
    #验证密码
    a = hashlib.md5()
    a.update((password + user.salt).encode("utf-8")) #将输入的密码重新加密
   # password = a.hexdigest()
    if(a.hexdigest()!=user.password):
        return redirect_with_msg('/regloginpage/', u'用户名的密码错误', 'reglogin')

    next=request.values.get('next')

    if next !=None and next.startswith('/'):
        return redirect(next)

    login_user(user)

    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


#upload the photos



@app.route('/upload/',methods={'POST'})
def upload():
    #file 所有请求过来关于文件的参数数据
    # print(type(request.files))
    # print(request.files)
    # <class 'werkzeug.datastructures.ImmutableMultiDict'>
    # ImmutableMultiDict([('', < FileStorage: '201903141343850.jpg' ('image/jpeg') >)])

    #file = request.files['file']

    #print(dir(file))

    # return 'ok'
    # 选择文件 send 返回ok

    file = request.files['file']
#     # http://werkzeug.pocoo.org/docs/0.10/datastructures/
#     # 需要对文件进行裁剪等操作
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower() #取文件扩展你名，用strip的方法取'.'右端的扩展名
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext #文件名随机值生成
        url = qiniu_upload_file(file, file_name)
        #url = save_to_local(file, file_name)
        if url != None:
            db.session.add(Image(url , current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)




@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


def save_to_local(file,file_name):
    save_dir= app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir,file_name))
    print(file_name)
    #已经传到路径
    return '/image/'+file_name

def save_to_qiniu(file, file_name):
    return qiniu_upload_file(file, file_name)


@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code":0, "id":comment.id,
                       "content":comment.content,
                       "username":comment.user.username,
                       "user_id":comment.user_id})
