# plugins/record/__init__.py
import os
import asyncio
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
import json

# 定义 Record 目录和记录状态文件（在插件目录内）
PLUGIN_DIR = os.path.dirname(__file__)
RECORD_DIR = os.path.join(PLUGIN_DIR, "records")
RECORDING_CHATS_FILE = os.path.join(PLUGIN_DIR, "recording_chats.json")

# 创建 Record 目录（如果不存在）
if not os.path.exists(RECORD_DIR):
    os.makedirs(RECORD_DIR)

# 全局变量，用于存储记录状态（聊天ID -> {"enabled": bool, "name": str}）
recording_chats = {}

# 加载已保存的 recording_chats
def load_recording_chats():
    global recording_chats
    if os.path.exists(RECORDING_CHATS_FILE):
        try:
            with open(RECORDING_CHATS_FILE, "r", encoding="utf-8") as f:
                recording_chats = json.load(f)
            # 转换键为整数
            recording_chats = {int(k): v for k, v in recording_chats.items()}
        except Exception as e:
            print(f"加载记录状态文件出错: {e}")
            recording_chats = {}
    else:
        recording_chats = {}

# 保存 recording_chats 到文件
def save_recording_chats():
    try:
        # 确保所有键都是字符串（JSON要求）
        data_to_save = {str(k): v for k, v in recording_chats.items()}
        with open(RECORDING_CHATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        print(f"保存记录状态: recording_chats={recording_chats}")
    except Exception as e:
        print(f"保存记录状态文件出错: {e}")

# 启动时加载记录状态
load_recording_chats()

async def process_record_request(client: Client, message: Message):
    """
    处理 ,record 命令，启用或禁用聊天消息记录
    用法：,record true 或 ,record false
    """
    chat_id = message.chat.id
    chat_title = message.chat.title if message.chat.title else f"Chat_{chat_id}"
    
    # 解析命令参数
    args = message.text.strip().split()
    
    if len(args) < 2 or args[1].lower() not in ["true", "false"]:
        await message.edit_text("用法：,record true 或 ,record false")
        await asyncio.sleep(2)
        await message.delete()
        return

    enable = args[1].lower() == "true"

    if enable:
        # 启用记录
        recording_chats[chat_id] = {
            "enabled": True,
            "name": chat_title
        }
        await message.edit_text(f"已启用群组「{chat_title}」的消息记录")
        print(f"启用记录: chat_id={chat_id}, name={chat_title}")
    else:
        # 禁用记录
        if chat_id in recording_chats:
            recording_chats[chat_id]["enabled"] = False
        else:
            recording_chats[chat_id] = {
                "enabled": False,
                "name": chat_title
            }
        await message.edit_text(f"已禁用群组「{chat_title}」的消息记录")
        print(f"禁用记录: chat_id={chat_id}, name={chat_title}")
    
    # 保存状态
    save_recording_chats()
    
    # 等待并删除消息
    await asyncio.sleep(2)
    await message.delete()

def get_safe_filename(name, chat_id):
    """
    生成安全的文件名：群聊名称+群聊id
    """
    # 替换文件名中不允许的字符
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-") if name else f"Chat_{chat_id}"
    # 限制文件名长度
    if len(safe_name) > 50:
        safe_name = safe_name[:50]
    return f"{safe_name}_{chat_id}.txt"

async def log_chat_messages(client: Client, message: Message):
    """
    记录聊天消息到文件，保存到插件目录内的 records 目录
    - 对单独群可以使用，record true或false开关记录
    - 不同的群记录保存为群聊名称+群聊id（如果群聊名称变了也依旧记录在同一个文件中）
    - 除文字外的内容，则用[图片]、[表情包]这种替代
    - 包含用户名和真实姓名（如果有）
    - 如果是频道发言，记录频道名称
    - 时间戳使用 UTC+8
    """
    chat_id = message.chat.id
    
    # 检查是否启用记录
    if chat_id not in recording_chats or not recording_chats[chat_id].get("enabled", False):
        return

    # 获取群组名称（使用记录时的名称）
    chat_name = recording_chats[chat_id].get("name", f"Chat_{chat_id}")
    
    # 获取发送者信息
    sender_id = "匿名"
    sender_username = ""
    sender_full_name = ""
    
    if message.from_user:
        sender_id = f"User:{message.from_user.id}"
        sender_username = f"@{message.from_user.username}" if message.from_user.username else ""
        # 使用 first_name 和 last_name 组合
        first_name = getattr(message.from_user, 'first_name', '')
        last_name = getattr(message.from_user, 'last_name', '')
        # 只有当 last_name 不为空时才组合
        if last_name:
            sender_full_name = f"{first_name} {last_name}".strip()
        else:
            sender_full_name = first_name.strip()
    elif message.sender_chat:
        sender_id = f"Channel:{message.sender_chat.id}"
        sender_full_name = message.sender_chat.title if message.sender_chat.title else ""

    # 获取 UTC+8 时间
    utc8_offset = timedelta(hours=8)
    timestamp = datetime.now(timezone.utc).astimezone(timezone(utc8_offset)).strftime("%Y-%m-%d %H:%M:%S")

    # 判断消息类型并设置记录内容
    if message.photo:
        text = "[图片]"
        # 如果有 caption，附加到文本中
        if message.caption:
            text += f" {message.caption}"
    elif message.sticker:
        text = "[表情包]"
    elif message.document:
        text = "[文件]"
    elif message.video:
        text = "[视频]"
    elif message.animation:
        text = "[动图]"
    elif message.audio:
        text = "[音频]"
    elif message.voice:
        text = "[语音]"
    else:
        text = message.text or "[无文本]"

    # 处理消息中的超链接
    entities = message.entities or message.caption_entities or []
    for entity in entities:
        if entity.type == "text_link" and entity.url:
            text += f" (链接: {entity.url})"
        elif entity.type == "url":
            url = text[entity.offset:entity.offset + entity.length]
            text += f" (链接: {url})"

    # 格式化记录
    log_entry = f"[{timestamp}][{sender_id}][@{sender_username}][{sender_full_name}]: {text}\n"

    # 生成文件名：群聊名称+群聊id
    filename = os.path.join(RECORD_DIR, get_safe_filename(chat_name, chat_id))

    # 保存到文件
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"记录消息: [{timestamp}][{sender_id}][@{sender_username}][{sender_full_name}]: {text}")
    except Exception as e:
        print(f"保存记录时出错: {e}")