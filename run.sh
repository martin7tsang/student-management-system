#!/bin/bash
# 运行学生管理系统（使用不同端口）

# 方法1: 使用 5001 端口
python3 app.py --port=5001

# 或者方法2: 修改代码中的端口
# 在 app.py 最后一行改成：
# app.run(debug=True, host='0.0.0.0', port=5001)
