import asyncio
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

async def process_jupai_request(client: Client, message: Message):
    """处理 jupai 命令，从API获取举牌小人图片并回复"""
    # 获取用户输入的文本
    text = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ""
    
    if not text:
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text="请提供要生成举牌小人图片的文本",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        # 构造API请求URL
        ju_pai_api = "https://api.txqq.pro/api/zt.php"
        image_url = f"{ju_pai_api}?msg={urllib.parse.quote(text)}"
        
        # 发送图片
        await client.send_photo(
            chat_id=message.chat.id,
            photo=image_url
        )
        
        # 删除原始消息
        await client.delete_messages(chat_id=message.chat.id, message_ids=message.id)
        
    except Exception as e:
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=f"发生错误: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )