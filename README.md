# Student Management System
# 学生管理系统

一个基于 Flask + Bootstrap 5 的完整学生信息管理系统。

## 功能特性

- ✅ 用户登录认证
- ✅ 学生信息管理（增删改查）
- ✅ 课程信息管理
- ✅ 成绩录入与查询
- ✅ 数据统计与可视化
- ✅ 响应式设计，支持移动端

## 技术栈

- **后端**: Python + Flask
- **数据库**: SQLite
- **前端**: HTML5 + Bootstrap 5 + Bootstrap Icons
- **ORM**: Flask-SQLAlchemy
- **认证**: Flask-Login

## 安装运行

### 1. 克隆仓库
```bash
git clone https://github.com/martin7tsang/student-management-system.git
cd student-management-system
```

### 2. 安装依赖
```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

### 3. 运行应用
```bash
python app.py
```

### 4. 访问系统
打开浏览器访问: http://localhost:5000

**默认登录账号:**
- 用户名: admin
- 密码: admin123

## 功能模块

### 学生管理
- 添加、编辑、删除学生信息
- 支持学号、姓名、性别、年龄、联系方式等字段
- 搜索功能

### 课程管理
- 添加、编辑、删除课程
- 课程代码、名称、学分、授课教师

### 成绩管理
- 录入学生成绩
- 按学生或课程筛选查看
- 成绩等级显示（优秀/良好/及格/不及格）
- 自动计算平均分

## 项目结构

```
student-management-system/
├── app.py              # 主应用文件
├── README.md           # 项目说明
├── requirements.txt    # 依赖列表
├── static/            # 静态文件
└── templates/         # HTML模板
    ├── base.html      # 基础模板
    ├── login.html     # 登录页
    ├── index.html     # 首页仪表板
    ├── students.html  # 学生列表
    ├── add_student.html
    ├── courses.html   # 课程列表
    ├── add_course.html
    ├── grades.html    # 成绩列表
    └── add_grade.html
```

## 安全说明

- 密码使用 werkzeug 进行哈希存储
- 使用 Flask-Login 管理用户会话
- 数据库使用 SQLite，适合中小型应用

## 未来改进

- [ ] 数据导出功能（Excel/PDF）
- [ ] 成绩统计分析图表
- [ ] 多用户权限管理
- [ ] 数据库迁移到 PostgreSQL/MySQL

## License

MIT
