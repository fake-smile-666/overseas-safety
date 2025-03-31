import pandas as pd
import os
import random
from datetime import datetime

def get_countries():
    """获取所有国家列表"""
    try:
        df = pd.read_csv('data/risk_data.csv')
        return df['country'].tolist()
    except Exception as e:
        return []

def get_country_risk_level(country):
    """获取国家风险等级"""
    try:
        df = pd.read_csv('data/risk_data.csv')
        country_data = df[df['country'] == country].iloc[0]
        
        return {
            'overall': country_data['risk_level'],
            'crime': country_data['crime_risk'],
            'terrorism': country_data['terrorism_risk'],
            'health': country_data['health_risk'],
            'natural_disaster': country_data['natural_disaster_risk'],
            'transportation': country_data['transportation_risk']
        }
    except Exception as e:
        # 返回默认值，确保字段完整
        return {
            'overall': 3,
            'crime': 3,
            'terrorism': 3,
            'health': 3,
            'natural_disaster': 3,
            'transportation': 3
        }

def get_safety_tips(risk_level, city_risk=None, season=None):
    """获取安全建议"""
    tips = {
        'general': [],
        'specific': []
    }
    
    # 通用安全建议
    tips['general'].extend([
        "保持警惕,注意周围环境",
        "随身携带重要证件和联系方式",
        "避免携带大量现金",
        "保持与家人朋友的联系",
        "了解当地紧急求助电话"
    ])
    
    # 根据总体风险等级添加建议
    if risk_level['overall'] >= 4:
        tips['general'].extend([
            "建议非必要不要前往",
            "如必须前往,请提前做好充分准备",
            "避免单独行动",
            "保持低调,避免引起注意"
        ])
    elif risk_level['overall'] >= 3:
        tips['general'].extend([
            "提高警惕,注意安全",
            "避免前往偏僻地区",
            "注意保管好随身物品",
            "遵守当地法律法规"
        ])
    
    # 根据具体风险类别添加建议
    if risk_level['crime'] >= 4:
        tips['specific'].extend([
            "避免夜间单独外出",
            "不要携带贵重物品",
            "注意防范抢劫和盗窃",
            "避免前往治安较差的区域"
        ])
    
    if risk_level['terrorism'] >= 4:
        tips['specific'].extend([
            "避免前往人群密集场所",
            "注意可疑人员和物品",
            "了解当地安全预警信息",
            "保持与使领馆的联系"
        ])
    
    if risk_level['health'] >= 4:
        tips['specific'].extend([
            "提前接种必要的疫苗",
            "携带常用药品",
            "注意饮食卫生",
            "避免饮用生水"
        ])
    
    if risk_level['natural_disaster'] >= 4:
        tips['specific'].extend([
            "了解当地自然灾害风险",
            "关注天气预报和预警信息",
            "准备应急物资",
            "制定应急撤离计划"
        ])
    
    if risk_level['transportation'] >= 4:
        tips['specific'].extend([
            "选择正规交通工具",
            "避免夜间出行",
            "注意交通安全",
            "提前了解交通规则"
        ])
    
    # 如果提供了城市风险评估,添加城市特定建议
    if city_risk:
        try:
            if city_risk['overall'] > risk_level['overall']:
                tips['specific'].extend([
                    f"注意: {city_risk['city']}的风险等级高于该国平均水平",
                    "建议提高警惕,加强防范措施",
                    "避免前往高风险区域"
                ])
                
            # 添加城市特定风险提示
            if city_risk['crime'] >= 4:
                tips['specific'].append(f"{city_risk['city']}的犯罪风险较高，请格外注意人身财产安全")
                
            if city_risk['natural_disaster'] >= 3:
                tips['specific'].append(f"{city_risk['city']}的自然灾害风险较高，请关注当地预警信息")
        except Exception as e:
            # 如果city_risk缺少某些键，也不会导致整个功能失败
            pass
    
    # 根据季节添加建议
    if season:
        if season == 'summer':
            tips['specific'].extend([
                "注意防暑降温",
                "避免长时间户外活动",
                "注意防晒",
                "多补充水分"
            ])
        elif season == 'winter':
            tips['specific'].extend([
                "注意保暖",
                "预防感冒",
                "注意路面结冰",
                "准备防寒装备"
            ])
        elif season == 'spring':
            tips['specific'].extend([
                "注意花粉过敏",
                "防范季节性流感",
                "关注天气变化",
                "准备雨具"
            ])
        elif season == 'autumn':
            tips['specific'].extend([
                "准备适当衣物应对温差",
                "注意秋季传染病预防",
                "关注台风等季节性天气",
                "注意早晚温差"
            ])
    
    return tips 