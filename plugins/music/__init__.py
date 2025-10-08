""" 网易云音乐插件 """

import asyncio
from pyrogram import filters
from pyrogram.errors import YouBlockedUser
from pyrogram.types import Message
from typing import Optional

# 插件帮助信息
MUSIC_HELP_MSG = """
网易云搜/点歌。
用法:
`,music 失眠飞行 兔籽鲸`  - 通过歌曲名称+歌手（可选）点歌
`,music https://music.163.com/#/song?id=1430702717`  - 通过歌曲链接点歌
`,music 1430702717`  - 通过歌曲 ID 点歌
"""

async def start_music_bot(client, message: Message) -> bool:
    """启动与Music163bot的对话"""
    try:
        await client.send_message("Music163bot", "/start")
        return True
    except YouBlockedUser:
        # 如果被阻止，先解除阻止再发送
        await client.unblock_user("Music163bot")
        await client.send_message("Music163bot", "/start")
        return True
    except Exception as e:
        await message.edit_text(f"无法启动Music163bot: {str(e)}")
        return False

async def search_music(client, keyword: str, message: Message):
    """通过关键词搜索音乐"""
    try:
        # 发送搜索命令
        await client.send_message("Music163bot", f"/search {keyword}")
        
        # 等待并获取搜索结果（使用更通用的方法）
        # 等待几秒钟让机器人响应
        await asyncio.sleep(3)
        
        # 获取最新的来自Music163bot的消息
        async for msg in client.get_chat_history("Music163bot", limit=5):
            if msg.from_user and msg.from_user.username == "Music163bot":
                # 检查是否是搜索结果
                if msg.reply_markup and len(msg.reply_markup.inline_keyboard) > 0:
                    # 点击第一个按钮
                    await client.request_callback_answer(
                        msg.chat.id,
                        msg.id,
                        callback_data=msg.reply_markup.inline_keyboard[0][0].callback_data,
                    )
                    break
                elif msg.audio:
                    # 直接收到了音频文件
                    # 检查message_thread_id是否存在
                    copy_kwargs = {
                        "chat_id": message.chat.id,
                        "reply_to_message_id": message.reply_to_message_id
                    }
                    if hasattr(message, 'message_thread_id') and message.message_thread_id:
                        copy_kwargs["message_thread_id"] = message.message_thread_id
                    
                    await msg.copy(**copy_kwargs)
                    await message.delete()
                    return
        
        # 再次等待并获取音频文件
        await asyncio.sleep(3)
        async for msg in client.get_chat_history("Music163bot", limit=5):
            if msg.from_user and msg.from_user.username == "Music163bot" and msg.audio:
                # 检查message_thread_id是否存在
                copy_kwargs = {
                    "chat_id": message.chat.id,
                    "reply_to_message_id": message.reply_to_message_id
                }
                if hasattr(message, 'message_thread_id') and message.message_thread_id:
                    copy_kwargs["message_thread_id"] = message.message_thread_id
                
                await msg.copy(**copy_kwargs)
                await message.delete()
                return
        
        # 如果没有找到结果
        await message.edit_text("未找到相关音乐，请检查搜索关键词。")
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.edit_text(f"搜索音乐时出错: {str(e)}")
        await asyncio.sleep(5)
        await message.delete()

async def get_music_by_url(client, url: str, message: Message):
    """通过URL获取音乐"""
    try:
        # 发送URL
        await client.send_message("Music163bot", url)
        
        # 等待并获取音频文件
        await asyncio.sleep(3)
        async for msg in client.get_chat_history("Music163bot", limit=5):
            if msg.from_user and msg.from_user.username == "Music163bot" and msg.audio:
                # 检查message_thread_id是否存在
                copy_kwargs = {
                    "chat_id": message.chat.id,
                    "reply_to_message_id": message.reply_to_message_id
                }
                if hasattr(message, 'message_thread_id') and message.message_thread_id:
                    copy_kwargs["message_thread_id"] = message.message_thread_id
                
                await msg.copy(**copy_kwargs)
                await message.delete()
                return
        
        await message.edit_text("无法通过URL获取音乐。")
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.edit_text(f"通过URL获取音乐时出错: {str(e)}")
        await asyncio.sleep(5)
        await message.delete()

async def get_music_by_id(client, music_id: str, message: Message):
    """通过ID获取音乐"""
    try:
        # 发送音乐ID
        await client.send_message("Music163bot", f"/music {music_id}")
        
        # 等待并获取音频文件
        await asyncio.sleep(3)
        async for msg in client.get_chat_history("Music163bot", limit=5):
            if msg.from_user and msg.from_user.username == "Music163bot" and msg.audio:
                # 检查message_thread_id是否存在
                copy_kwargs = {
                    "chat_id": message.chat.id,
                    "reply_to_message_id": message.reply_to_message_id
                }
                if hasattr(message, 'message_thread_id') and message.message_thread_id:
                    copy_kwargs["message_thread_id"] = message.message_thread_id
                
                await msg.copy(**copy_kwargs)
                await message.delete()
                return
        
        await message.edit_text("无法通过ID获取音乐。")
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.edit_text(f"通过ID获取音乐时出错: {str(e)}")
        await asyncio.sleep(5)
        await message.delete()

async def process_music_request(client, message: Message):
    """
    处理音乐请求
    用法：
    ,music 歌曲名 [歌手]  - 搜索音乐
    ,music https://...     - 通过链接获取音乐
    ,music 123456         - 通过ID获取音乐
    """
    # 检查是否有参数
    if not message.text or len(message.text.strip().split()) < 2:
        await message.edit_text(MUSIC_HELP_MSG)
        await asyncio.sleep(10)
        await message.delete()
        return
    
    # 获取参数
    args = message.text.strip().split(maxsplit=1)
    if len(args) < 2:
        await message.edit_text(MUSIC_HELP_MSG)
        await asyncio.sleep(10)
        await message.delete()
        return
    
    query = args[1].strip()
    
    # 启动与Music163bot的对话
    if not await start_music_bot(client, message):
        return
    
    # 根据参数类型处理请求
    if query.startswith("http"):
        # URL方式
        await get_music_by_url(client, query, message)
    elif query.isdigit():
        # ID方式
        await get_music_by_id(client, query, message)
    else:
        # 搜索方式
        await search_music(client, query, message)