import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

async def process_info_request(client: Client, message: Message):
    """处理 info 命令，显示用户信息或群组信息"""
    try:
        msg = message.reply_to_message
        if msg and msg.from_user:  # 检查是否有回复消息且来自用户
            user = msg.from_user
            if user.id:
                if user.username:
                    response = f"用户名：[{user.username}](https://t.me/{user.username})\n" \
                               f"UserID：`{user.id}`\n" \
                               f"DC：{user.dc_id}\n" \
                               f"大会员：{user.is_premium}"
                else:
                    response = f"用户名：None\n" \
                               f"UserID：`{user.id}`\n" \
                               f"DC：{user.dc_id}\n" \
                               f"大会员：{user.is_premium}"
                sent_message = await message.reply(response)
                await message.delete()  # 删除用户命令消息
                await asyncio.sleep(10)  # 等待10秒
                await sent_message.delete()  # 删除回复消息
        elif msg and msg.sender_chat:  # 检查是否有回复消息且来自群组
            chat = msg.sender_chat
            if chat.id:
                response = f"群组：{chat.title}\n" \
                           f"ChatID：`{chat.id}`\n"
                sent_message = await message.reply(response)
                await message.delete()  # 删除用户命令消息
                await asyncio.sleep(10)  # 等待10秒
                await sent_message.delete()  # 删除回复消息
        else:  # 如果没有回复消息，显示当前聊天信息
            if message.chat:
                chat_info = message.chat
                if chat_info.id:
                    response = f"群组：{chat_info.title}\n" \
                               f"ChatID：`{chat_info.id}`\n"
                    sent_message = await message.reply(response)
                    await message.delete()  # 删除用户命令消息
                    await asyncio.sleep(10)  # 等待10秒
                    await sent_message.delete()  # 删除回复消息
            else:
                sent_message = await message.reply("无法获取信息，请在群组中使用或回复一条消息")
                await message.delete()
                await asyncio.sleep(1)
                await sent_message.delete()
    except Exception as e:
        # 异常情况下显示当前聊天信息
        if message.chat:
            chat_info = message.chat
            if chat_info.id:
                response = f"群组：{chat_info.title}\n" \
                           f"ChatID：`{chat_info.id}`\n"
                sent_message = await message.reply(response)
                await message.delete()  # 删除用户命令消息
                await asyncio.sleep(10)  # 等待10秒
                await sent_message.delete()  # 删除回复消息
        else:
            sent_message = await message.reply("发生错误，无法获取信息")
            await message.delete()
            await asyncio.sleep(1)
            await sent_message.delete()

async def process_emoji_info_request(client: Client, message: Message):
    """处理 emoji_info 命令，获取回复消息中的自定义表情 ID"""
    if message.reply_to_message and message.reply_to_message.entities:
        custom_emoji_ids = [entity.custom_emoji_id for entity in message.reply_to_message.entities if entity.custom_emoji_id]
        if custom_emoji_ids:
            response = f"`{custom_emoji_ids}`"
        else:
            response = "没有找到自定义表情"
    else:
        response = "笨蛋，这不是emoji"
    sent_message = await message.reply(response)
    await message.delete()  # 删除用户命令消息
    await asyncio.sleep(10)  # 等待10秒
    await sent_message.delete()  # 删除回复消息