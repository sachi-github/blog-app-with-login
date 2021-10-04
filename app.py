from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import pytz

app = Flask(__name__)
# データメース作るときの決まり文句
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# データベース作成
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))

# flask_loginを使うために必要な記述
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def top():
    return render_template('top.html')

# メイン機能
@app.route('/index', methods=['GET', 'POST'])
@login_required                             # ログインしているユーザーしかアクセスできない
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)

# サインアップ（新規登録）機能
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # blog.dbのusernameとpasswordにsignup()関数内のusernameとpasswordをw渡す
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(user) # 追加
        db.session.commit()  # 変更を保存

        return redirect('/login')

    else:
        return render_template('signup.html')

# ログイン機能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
        # blog.dbのusernameとpasswordにsignup()関数内のusernameとpasswordをw渡す
        user = User.query.filter_by(username=username).first()
        print(user)
        
        if user == None or user.username != username or not check_password_hash(user.password, password):
            return render_template('login.html', correct=False) 
        else:
            login_user(user)
            return redirect('/index')  

    else:
        return render_template('login.html')

# ログアウト機能
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# ブログの新規作成機能
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        # blog.dbのtitleとbodyにcreate()関数内のtitleとbodyをw渡す
        post = Post(title=title, body=body)
        db.session.add(post) # 追加
        db.session.commit()  # 変更を保存

        return redirect('/index')

    else:
        return render_template('create.html')

# ブログの更新機能
@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        # 更新の際はpostとaddは不要
        db.session.commit()  # 変更を保存

        return redirect('/index')

# ブログ削除機能
@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)    
    db.session.delete(post)
    db.session.commit()

    return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True)