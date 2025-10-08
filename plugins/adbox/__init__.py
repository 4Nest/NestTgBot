""" Adbox插件 - 发送/mysterybox命令指定次数 """

import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message

async def process_adbox_request(client: Client, message: Message):
    """
    处理adbox命令：
    格式：adbox n*m
    n要≤10，然后发送/mysterybox n消息m次，每次间隔1秒
    """
    try:
        # 解析命令参数
        command_text = message.text.strip()
        # 使用正则表达式匹配 'adbox n*m' 格式
        pattern = r'^[,，]adbox\s+(\d+)\*(\d+)$'
        match = re.match(pattern, command_text)
        
        if not match:
            await message.edit_text("命令格式错误，请使用: adbox n*m (n≤10)")
            await asyncio.sleep(3)
            await message.delete()
            return
        
        # 提取n和m参数
        n = int(match.group(1))
        m = int(match.group(2))
        
        # 检查n是否≤10
        if n > 10:
            await message.edit_text("参数n必须≤10")
            await asyncio.sleep(3)
            await message.delete()
            return
        
        # 发送/mysterybox n消息m次，每次间隔1秒
        for i in range(m):
            await client.send_message(
                chat_id=message.chat.id,
                text=f"/mysterybox {n}"
            )
            # 如果不是最后一次发送，等待1秒
            if i < m - 1:
                await asyncio.sleep(1)
        
        # 完成后删除原消息
            
    except ValueError:
        await message.edit_text("参数必须是数字")
        await asyncio.sleep(3)
        await message.delete()
    except Exception as e:
        await message.edit_text(f"处理请求时出错: {str(e)}")
        await asyncio.sleep(3)
        await message.delete()

# 插件帮助信息
HELP_MESSAGE = """
/adbox n*m - 发送/mysterybox n消息m次，每次间隔1秒 (n≤10)
"""