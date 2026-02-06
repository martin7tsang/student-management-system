# Student Management System
# 学生管理系统

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-management-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 学生模型
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联成绩
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')

# 课程模型
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    teacher = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联成绩
    grades = db.relationship('Grade', backref='course', lazy=True, cascade='all, delete-orphan')

# 成绩模型
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Float)
    exam_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束：一个学生同一门课程只有一个成绩
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 初始化数据库和默认用户
def init_db():
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账号
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员账号创建成功")
            print("   用户名: admin")
            print("   密码: admin123")

# 路由：首页
@app.route('/')
@login_required
def index():
    # 统计数据
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_grades = Grade.query.count()
    
    # 最近添加的学生
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_students=total_students,
                         total_courses=total_courses,
                         total_grades=total_grades,
                         recent_students=recent_students)

# 路由：登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')

# 路由：登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))

# ========== 学生管理 ==========

@app.route('/students')
@login_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Student.query
    if search:
        query = query.filter(Student.name.contains(search) | 
                           Student.student_id.contains(search))
    
    students = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('students.html', students=students, search=search)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        student = Student(
            student_id=request.form['student_id'],
            name=request.form['name'],
            gender=request.form['gender'],
            age=request.form.get('age', type=int),
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address']
        )
        
        try:
            db.session.add(student)
            db.session.commit()
            flash('学生添加成功！', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('add_student.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        student.student_id = request.form['student_id']
        student.name = request.form['name']
        student.gender = request.form['gender']
        student.age = request.form.get('age', type=int)
        student.email = request.form['email']
        student.phone = request.form['phone']
        student.address = request.form['address']
        
        try:
            db.session.commit()
            flash('学生信息更新成功！', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('edit_student.html', student=student)

@app.route('/students/delete/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    
    try:
        db.session.delete(student)
        db.session.commit()
        flash('学生删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('students'))

# ========== 课程管理 ==========

@app.route('/courses')
@login_required
def courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('courses.html', courses=courses)

@app.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        course = Course(
            course_code=request.form['course_code'],
            name=request.form['name'],
            description=request.form['description'],
            credits=request.form.get('credits', type=int),
            teacher=request.form['teacher']
        )
        
        try:
            db.session.add(course)
            db.session.commit()
            flash('课程添加成功！', 'success')
            return redirect(url_for('courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('add_course.html')

@app.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    
    if request.method == 'POST':
        course.course_code = request.form['course_code']
        course.name = request.form['name']
        course.description = request.form['description']
        course.credits = request.form.get('credits', type=int)
        course.teacher = request.form['teacher']
        
        try:
            db.session.commit()
            flash('课程更新成功！', 'success')
            return redirect(url_for('courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('edit_course.html', course=course)

@app.route('/courses/delete/<int:id>')
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    
    try:
        db.session.delete(course)
        db.session.commit()
        flash('课程删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('courses'))

# ========== 成绩管理 ==========

@app.route('/grades')
@login_required
def grades():
    page = request.args.get('page', 1, type=int)
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    
    query = Grade.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    grades = query.paginate(page=page, per_page=15, error_out=False)
    students = Student.query.all()
    courses = Course.query.all()
    
    return render_template('grades.html', 
                         grades=grades, 
                         students=students, 
                         courses=courses,
                         selected_student=student_id,
                         selected_course=course_id)

@app.route('/grades/add', methods=['GET', 'POST'])
@login_required
def add_grade():
    if request.method == 'POST':
        grade = Grade(
            student_id=request.form.get('student_id', type=int),
            course_id=request.form.get('course_id', type=int),
            score=request.form.get('score', type=float),
            exam_date=datetime.strptime(request.form['exam_date'], '%Y-%m-%d').date() if request.form['exam_date'] else None
        )
        
        try:
            db.session.add(grade)
            db.session.commit()
            flash('成绩录入成功！', 'success')
            return redirect(url_for('grades'))
        except Exception as e:
            db.session.rollback()
            flash(f'录入失败：{str(e)}', 'danger')
    
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('add_grade.html', students=students, courses=courses)

@app.route('/grades/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_grade(id):
    grade = Grade.query.get_or_404(id)
    
    if request.method == 'POST':
        grade.score = request.form.get('score', type=float)
        grade.exam_date = datetime.strptime(request.form['exam_date'], '%Y-%m-%d').date() if request.form['exam_date'] else None
        
        try:
            db.session.commit()
            flash('成绩更新成功！', 'success')
            return redirect(url_for('grades'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('edit_grade.html', grade=grade)

@app.route('/grades/delete/<int:id>')
@login_required
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    
    try:
        db.session.delete(grade)
        db.session.commit()
        flash('成绩删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('grades'))

# 学生成绩统计
@app.route('/students/<int:id>/grades')
@login_required
def student_grades(id):
    student = Student.query.get_or_404(id)
    grades = Grade.query.filter_by(student_id=id).all()
    
    # 计算平均成绩
    if grades:
        avg_score = sum(g.score for g in grades if g.score) / len(grades)
    else:
        avg_score = 0
    
    return render_template('student_grades.html', 
                         student=student, 
                         grades=grades, 
                         avg_score=avg_score)

if __name__ == '__main__':
    init_db()
    print("🚀 启动学生管理系统...")
    print("📱 访问地址: http://localhost:5000")
    print("🔑 默认账号: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)
