""" Help插件 - 显示所有加载的插件及其功能 """

import json
import os
from pyrogram import Client, filters
from pyrogram.types import Message

# 插件功能描述文件路径
PLUGIN_DESCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), "plugin_descriptions.json")

# 默认插件功能描述
DEFAULT_PLUGIN_DESCRIPTIONS = {
    "music": "网易云音乐搜索和播放插件，支持通过歌曲名、链接或ID搜索音乐",
    "record": "聊天记录插件，可以记录群聊消息到文件",
    "say": "文字转语音插件，将文字消息转换为语音发送",
    "ad": "广告插件，用于发送广告信息",
    "crazy4": "Crazy4游戏插件",
    "jupai": "举牌插件",
    "touch": "触摸插件",
    "help": "帮助插件，显示所有加载的插件及其功能"
}

async def load_plugin_descriptions():
    """加载插件功能描述"""
    if os.path.exists(PLUGIN_DESCRIPTIONS_FILE):
        try:
            with open(PLUGIN_DESCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_PLUGIN_DESCRIPTIONS
    else:
        # 如果文件不存在，创建默认文件
        try:
            with open(PLUGIN_DESCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_PLUGIN_DESCRIPTIONS, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return DEFAULT_PLUGIN_DESCRIPTIONS

async def process_help_request(client: Client, message: Message):
    """处理help命令，显示所有加载的插件及其功能"""
    try:
        # 加载插件功能描述
        descriptions = await load_plugin_descriptions()
        
        # 构建帮助信息
        help_text = "🤖 可用插件列表:\n\n"
        
        # 获取插件目录
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
        if os.path.exists(plugins_dir):
            # 遍历插件目录
            for item in os.listdir(plugins_dir):
                plugin_path = os.path.join(plugins_dir, item)
                # 检查是否为目录且包含__init__.py文件
                if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "__init__.py")):
                    # 获取插件功能描述
                    description = descriptions.get(item, f"{item}插件")
                    help_text += f"🔹 {item}: {description}\n"
        
        # 发送帮助信息
        await message.edit_text(help_text)
        
        # 等待一段时间后删除消息
        import asyncio
        await asyncio.sleep(30)
        await message.delete()
        
    except Exception as e:
        await message.edit_text(f"获取插件信息时出错: {str(e)}")
        import asyncio
        await asyncio.sleep(5)
        await message.delete()

# 插件帮助信息
HELP_MESSAGE = """
/help - 显示所有加载的插件及其功能
"""