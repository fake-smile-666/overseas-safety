import bcrypt
import uuid
from datetime import datetime

class User:
    def __init__(self, username, email, emergency_contact, id=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.emergency_contact = emergency_contact
        self.password_hash = None
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def set_password(self, password):
        """设置用户密码，并进行哈希处理"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self, password):
        """验证用户密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'emergency_contact': self.emergency_contact,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建用户对象"""
        user = cls(
            username=data['username'],
            email=data['email'],
            emergency_contact=data['emergency_contact'],
            id=data['id'],
            created_at=data['created_at']
        )
        user.password_hash = data['password_hash']
        return user 