""" Q插件 - 转发消息到@GLBetabot并获取回复 """

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError

async def process_q_request(client: Client, message: Message):
    """
    处理q命令：
    1. 获取被回复消息的用户ID
    2. 转发被回复的消息到@GLBetabot
    3. 回复被转发的消息 /o userid
    4. 等待@GLBetabot的回复
    5. 将回复的sticker转发回原群组
    6. 如果超过10秒没有回复，则编辑原消息为"妙妙似了，q不出来"
    """
    try:
        # 检查是否是回复消息
        if not message.reply_to_message:
            await message.edit_text("请回复一条消息来使用此功能")
            await asyncio.sleep(3)
            await message.delete()
            return
        
        
        # 转发被回复的消息到@GLBetabot
        forwarded_msg = await message.reply_to_message.forward("@GLBetabot")
        
        # 回复被转发的消息，发送 /o userid
        command_msg = await client.send_message(
            chat_id="@GLBetabot",
            text=f"/o",
            reply_to_message_id=forwarded_msg.id
        )
        
        # 等待@GLBetabot的回复（最多10秒）
        async def wait_for_response():
            async for msg in client.get_chat_history("@GLBetabot", limit=10):
                # 检查是否是回复给/o命令消息的sticker
                if (msg.reply_to_message_id == command_msg.id and 
                    (msg.sticker or msg.text) and 
                    msg.from_user and msg.from_user.username == "GLBetabot"):
                    return msg
            return None
        
        # 等待回复，超时10秒
        response_msg = None
        for _ in range(10):  # 10次循环，每次等待1秒
            response_msg = await wait_for_response()
            if response_msg:
                break
            await asyncio.sleep(1)
        
        if response_msg:
            # 将回复的sticker或消息转发回原群组
            if hasattr(message, 'message_thread_id') and message.message_thread_id:
                await response_msg.copy(
                    chat_id=message.chat.id,
                    message_thread_id=message.message_thread_id
                )
            else:
                await response_msg.copy(chat_id=message.chat.id)
            
            # 删除原消息
            await message.delete()
        else:
            # 超时，编辑原消息
            await message.edit_text("妙妙似了，q不出来")
            await asyncio.sleep(3)
            await message.delete()
            
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_text("请求过于频繁，请稍后再试")
        await asyncio.sleep(3)
        await message.delete()
    except RPCError as e:
        await message.edit_text(f"RPC错误: {str(e)}")
        await asyncio.sleep(3)
        await message.delete()
    except Exception as e:
        await message.edit_text(f"处理请求时出错: {str(e)}")
        await asyncio.sleep(3)
        await message.delete()

# 插件帮助信息
HELP_MESSAGE = """
/q - 回复一条消息使用，将消息转发给@GLBetabot并获取回复
"""