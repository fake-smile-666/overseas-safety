import json
import os

def get_emergency_contacts(country_name=None):
    """获取紧急联系人信息
    
    参数:
        country_name (str, optional): 国家名称，如果不提供则返回所有国家信息
        
    返回:
        dict: 紧急联系人信息字典
    """
    try:
        # 确保紧急联系信息文件存在
        if not os.path.exists('data/emergency_info.json'):
            return {}
        
        with open('data/emergency_info.json', 'r', encoding='utf-8') as f:
            emergency_info = json.load(f)
        
        if country_name:
            return emergency_info.get(country_name, {})
        else:
            return emergency_info
    except Exception as e:
        print(f"Error getting emergency contacts: {e}")
        return {}

def add_emergency_contact(name, phone, relationship, user_id):
    """为用户添加个人紧急联系人
    
    参数:
        name (str): 联系人姓名
        phone (str): 联系人电话
        relationship (str): 与联系人关系
        user_id (str): 用户ID
        
    返回:
        bool: 操作是否成功
    """
    try:
        contact_file = f'data/personal_contacts_{user_id}.json'
        
        contacts = []
        if os.path.exists(contact_file):
            with open(contact_file, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
        
        # 添加新联系人
        new_contact = {
            'name': name,
            'phone': phone,
            'relationship': relationship
        }
        
        contacts.append(new_contact)
        
        # 保存到文件
        with open(contact_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=4)
            
        return True
    except Exception as e:
        print(f"Error adding emergency contact: {e}")
        return False

def get_personal_emergency_contacts(user_id):
    """获取用户个人紧急联系人列表
    
    参数:
        user_id (str): 用户ID
        
    返回:
        list: 联系人列表
    """
    try:
        contact_file = f'data/personal_contacts_{user_id}.json'
        
        if not os.path.exists(contact_file):
            return []
            
        with open(contact_file, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
            
        return contacts
    except Exception as e:
        print(f"Error getting personal emergency contacts: {e}")
        return [] 