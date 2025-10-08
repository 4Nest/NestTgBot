# config_loader.py - 用于加载YAML配置文件

import yaml
import os

def load_config(config_file='config.yaml'):
    """
    加载YAML配置文件
    """
    # 获取配置文件的绝对路径
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")
    
    # 读取YAML配置文件
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    return config

# 加载配置
config = load_config()

# 提取配置值
API_ID = config['telegram']['api_id']
API_HASH = config['telegram']['api_hash']
MY_USER_ID = config['user']['my_user_id']
MY_CHANNEL_IDS = config['user']['my_channel_ids']
DEEPSEEK_API_KEY = config['deepseek']['api_key']
DEEPSEEK_BASE_URL = config['deepseek'].get('base_url', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = config['deepseek'].get('model', 'deepseek-ai/DeepSeek-V3')
XAI_API_KEY = config['xai']['api_key']
XAI_BASE_URL = config['xai'].get('base_url', 'https://api.x.ai/v1')