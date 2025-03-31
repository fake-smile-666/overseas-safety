from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
import json
import pandas as pd
from datetime import datetime
import folium
import bcrypt
import random
import string
import logging
from logging.handlers import RotatingFileHandler
from utils.risk_assessment import get_country_risk_level, get_safety_tips, get_countries
from utils.emergency import get_emergency_contacts
from models.user import User

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32)))
app.config['USERS_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'users.json')

# 设置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('海外安全助手应用启动')

# 处理favicon.ico请求
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 添加一个诊断页面
@app.route('/network-check')
def network_check():
    # 获取本机IP地址
    import socket
    hostname = socket.gethostname()
    try:
        # 获取本地IP地址
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "无法获取"
    
    return render_template('network_check.html', 
                          hostname=hostname,
                          local_ip=local_ip,
                          port=5000)

# 全局错误处理
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'页面未找到: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'服务器错误: {error}', exc_info=True)
    return render_template('500.html'), 500

# 初始化用户数据文件
if not os.path.exists('data'):
    os.makedirs('data')
    
if not os.path.exists(app.config['USERS_FILE']):
    with open(app.config['USERS_FILE'], 'w') as f:
        json.dump([], f)

# 主页
@app.route('/')
def index():
    logged_in = 'username' in session
    username = session.get('username', '')
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', logged_in=logged_in, username=username, update_time=update_time)

# 清除指定账号外的所有用户（仅用于开发和测试阶段）
@app.route('/admin/clear_users')
def clear_users():
    # 检查是否已登录
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    
    try:
        # 读取用户数据
        with open(app.config['USERS_FILE'], 'r', encoding='utf-8') as f:
            try:
                users = json.load(f)
            except:
                users = []
        
        # 只保留用户名为 "1" 且密码正确的用户
        preserved_users = [user for user in users if user['username'] == '1']
        
        # 如果没有找到指定用户，返回错误
        if not preserved_users:
            flash('未找到指定保留的用户账号')
            return redirect(url_for('index'))
        
        # 保存更新后的用户数据
        with open(app.config['USERS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(preserved_users, f, ensure_ascii=False, indent=4)
        
        # 记录操作日志
        app.logger.info(f'已清除除用户名为 "1" 以外的所有用户账号，共保留 {len(preserved_users)} 个账号')
        
        flash('已成功清除除了指定账号外的所有用户')
        return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f'清除用户账号时出错: {str(e)}')
        flash(f'清除用户账号失败: {str(e)}')
        return redirect(url_for('index'))

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 打印接收到的表单数据
        app.logger.info(f"接收到的表单数据: {request.form}")
        
        # 获取表单数据
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        
        # 打印获取到的各个字段值
        app.logger.info(f"用户名: {username}")
        app.logger.info(f"密码: {'已提供' if password else '未提供'}")
        app.logger.info(f"邮箱: {email}")
        app.logger.info(f"紧急联系人: {emergency_contact}")
        
        # 验证表单数据
        if not username or not password or not email or not emergency_contact:
            missing_fields = []
            if not username: missing_fields.append('用户名')
            if not password: missing_fields.append('密码')
            if not email: missing_fields.append('邮箱')
            if not emergency_contact: missing_fields.append('紧急联系人')
            flash(f'请填写以下必填字段: {", ".join(missing_fields)}')
            return redirect(url_for('register'))
        
        # 验证密码长度
        if len(password) < 8:
            flash('密码长度至少为8位')
            return redirect(url_for('register'))
        
        # 验证邮箱格式
        if '@' not in email or '.' not in email:
            flash('请输入有效的邮箱地址')
            return redirect(url_for('register'))
        
        # 检查用户是否已存在
        users = []
        with open(app.config['USERS_FILE'], 'r', encoding='utf-8') as f:
            try:
                users = json.load(f)
            except:
                users = []
                
        if any(user['username'] == username for user in users):
            flash('用户名已存在')
            return redirect(url_for('register'))
            
        if any(user['email'] == email for user in users):
            flash('该邮箱已被注册')
            return redirect(url_for('register'))
        
        # 创建新用户
        user = User(
            username=username, 
            email=email,
            emergency_contact=emergency_contact
        )
        user.set_password(password)
        
        users.append(user.to_dict())
        
        try:
            with open(app.config['USERS_FILE'], 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            app.logger.info(f'用户注册成功: {username}')
            flash('注册成功，请登录')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f'保存用户数据失败: {str(e)}')
            flash('注册失败，请稍后重试')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码')
            return redirect(url_for('login'))
        
        users = []
        with open(app.config['USERS_FILE'], 'r') as f:
            try:
                users = json.load(f)
            except:
                users = []
        
        user = next((user for user in users if user['username'] == username), None)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('登录成功')
            return redirect(url_for('index'))
        
        flash('用户名或密码错误')
        return redirect(url_for('login'))
    
    return render_template('login.html')

# 用户登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('已登出')
    return redirect(url_for('index'))

# 用户个人资料页面
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    
    # 获取用户信息
    user_id = session['user_id']
    users = []
    with open(app.config['USERS_FILE'], 'r') as f:
        try:
            users = json.load(f)
        except:
            users = []
    
    user = next((user for user in users if user['id'] == user_id), None)
    
    if not user:
        flash('用户不存在')
        return redirect(url_for('logout'))
    
    return render_template('profile.html', user=user)

# 风险评估页面
@app.route('/risk_assessment', methods=['GET', 'POST'])
def risk_assessment():
    if request.method == 'POST':
        country = request.form.get('country')
        city = request.form.get('city')
        season = request.form.get('season', 'summer')  # 默认为夏季
        
        if not country:
            flash('请选择国家', 'error')
            return redirect(url_for('risk_assessment'))
            
        app.logger.info(f'风险评估请求: 国家={country}, 城市={city}, 季节={season}')
            
        # 获取国家风险评估
        try:
            risk_level = get_country_risk_level(country)
            app.logger.info(f'国家风险评估结果: {risk_level}')
        except Exception as e:
            app.logger.error(f'获取国家风险评估失败: {str(e)}')
            flash('获取国家风险评估失败', 'error')
            return redirect(url_for('risk_assessment'))
        
        # 获取城市风险评估
        city_risk = None
        if city:
            try:
                df = pd.read_csv('data/city_risk_data.csv')
                city_data = df[(df['country'] == country) & (df['city'] == city)]
                if not city_data.empty:
                    city_data = city_data.iloc[0]
                    city_risk = {
                        'city': city,
                        'overall': round((int(city_data['crime_risk']) + int(city_data['terrorism_risk']) + 
                                        int(city_data['health_risk']) + int(city_data['natural_disaster_risk']) + 
                                        int(city_data['transportation_risk'])) / 5, 1),
                        'crime': int(city_data['crime_risk']),
                        'terrorism': int(city_data['terrorism_risk']),
                        'health': int(city_data['health_risk']),
                        'natural_disaster': int(city_data['natural_disaster_risk']),
                        'transportation': int(city_data['transportation_risk'])
                    }
                    app.logger.info(f'城市风险评估结果: {city_risk}')
                else:
                    app.logger.warning(f'未找到城市数据: 国家={country}, 城市={city}')
            except Exception as e:
                app.logger.error(f'获取城市风险评估失败: {str(e)}')
                flash(f'获取城市"{city}"风险评估失败: {str(e)}', 'error')
        
        # 获取安全建议
        try:
            safety_tips = get_safety_tips(risk_level, city_risk, season)
            app.logger.info(f'生成安全建议成功，共{len(safety_tips["general"])+len(safety_tips["specific"])}条')
        except Exception as e:
            app.logger.error(f'生成安全建议失败: {str(e)}')
            flash('生成安全建议失败', 'error')
            safety_tips = {"general": [], "specific": []}
        
        return render_template('risk_assessment.html', 
                             countries=get_countries(),
                             risk_level=risk_level,
                             city_risk=city_risk,
                             safety_tips=safety_tips,
                             country=country,
                             city=city)
    
    # GET请求，显示选择表单
    try:
        countries = get_countries()
        return render_template('risk_assessment.html', countries=countries)
    except Exception as e:
        app.logger.error(f'获取国家列表失败: {str(e)}')
        flash('加载风险评估页面失败', 'error')
        return redirect(url_for('index'))

# 紧急联系人页面
@app.route('/emergency_contacts')
def emergency_contacts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    users = []
    with open(app.config['USERS_FILE'], 'r') as f:
        users = json.load(f)
    
    user = next((user for user in users if user['id'] == session['user_id']), None)
    
    # 获取紧急联系人信息
    local_emergency = get_emergency_contacts()
    
    return render_template('emergency_contacts.html', 
                           personal_contact=user['emergency_contact'] if user else "",
                           local_emergency=local_emergency)

# 安全地图页面
@app.route('/safety_map')
def safety_map():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('safety_map.html')

# 安全提示页面
@app.route('/safety_tips')
def safety_tips():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取常见安全提示
    tips = {
        "个人安全": [
            "随时保持警惕，注意周围环境",
            "避免在陌生区域单独行动，特别是在夜间",
            "保管好个人物品和证件",
            "将重要证件复印并存储电子版"
        ],
        "交通安全": [
            "了解当地交通规则",
            "优先选择正规交通工具",
            "避免搭乘无牌照车辆",
            "在不熟悉的地区使用导航软件"
        ],
        "住宿安全": [
            "选择安全评价高的住宿地点",
            "不要轻易让陌生人进入住处",
            "确保门窗安全锁闭",
            "了解紧急出口位置"
        ],
        "网络安全": [
            "避免使用公共WiFi处理敏感信息",
            "使用VPN保护个人网络安全",
            "定期更新密码",
            "小心钓鱼网站和诈骗邮件"
        ]
    }
    
    return render_template('safety_tips.html', tips=tips)

@app.route('/get_cities/<country>')
def get_cities(country):
    try:
        df = pd.read_csv('data/city_risk_data.csv')
        cities = df[df['country'] == country]['city'].tolist()
        return jsonify(cities)
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    # 确保数据目录存在
    if not os.path.exists('data'):
        os.makedirs('data')
        
    # 初始化风险数据
    if not os.path.exists('data/risk_data.csv'):
        risk_data = {
            'country': ['美国', '英国', '加拿大', '澳大利亚', '日本', '德国', '法国', '新加坡'],
            'risk_level': [2, 2, 1, 1, 1, 2, 2, 1]  # 1-低风险, 2-中风险, 3-高风险
        }
        pd.DataFrame(risk_data).to_csv('data/risk_data.csv', index=False)
    
    # 初始化紧急联系信息
    if not os.path.exists('data/emergency_info.json'):
        emergency_info = {
            '美国': {"警察": "911", "救护车": "911", "火警": "911", "中国使领馆": "+1-202-495-2266"},
            '英国': {"警察": "999", "救护车": "999", "火警": "999", "中国使领馆": "+44-20-7299-4049"},
            '加拿大': {"警察": "911", "救护车": "911", "火警": "911", "中国使领馆": "+1-613-789-6225"},
            '澳大利亚': {"警察": "000", "救护车": "000", "火警": "000", "中国使领馆": "+61-2-6228-3999"},
            '日本': {"警察": "110", "救护车": "119", "火警": "119", "中国使领馆": "+81-3-3403-3388"},
            '德国': {"警察": "110", "救护车": "112", "火警": "112", "中国使领馆": "+49-30-27588-0"},
            '法国': {"警察": "17", "救护车": "15", "火警": "18", "中国使领馆": "+33-1-4963-1919"},
            '新加坡': {"警察": "999", "救护车": "995", "火警": "995", "中国使领馆": "+65-6418-0224"}
        }
        with open('data/emergency_info.json', 'w', encoding='utf-8') as f:
            json.dump(emergency_info, f, ensure_ascii=False, indent=4)
    
    # 创建测试账号
    if not os.path.exists(app.config['USERS_FILE']):
        with open(app.config['USERS_FILE'], 'w') as f:
            json.dump([], f)
    
    # 检查测试账号是否存在
    with open(app.config['USERS_FILE'], 'r') as f:
        users = json.load(f)
    
    test_user = {
        'id': 'test-user-id',
        'username': 'test',
        'email': 'test@example.com',
        'emergency_contact': '1234567890',
        'password_hash': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if not any(user['username'] == 'test' for user in users):
        users.append(test_user)
        with open(app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f)
    
    # 为了解决访问问题，同时确保 localhost 和局域网访问
    app.logger.info('应用启动于 0.0.0.0:5000，可通过局域网访问')
    app.run(host='0.0.0.0', port=5000, debug=True) 