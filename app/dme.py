from pyrogram import Client, filters
import asyncio

async def delete_messages(client, message):
    """删除用户或指定频道指定数量的最近消息"""
    # 获取命令参数
    command_parts = message.text.split()
    if len(command_parts) < 2 or not command_parts[1].isdigit():
        await message.reply("请提供有效的数字，例如：，dme 10")
        return

    count = int(command_parts[1])  # 要删除的消息数量
    chat_id = message.chat.id

    deleted_count = 0
    async for msg in client.get_chat_history(chat_id, limit=count + 1):  # +1 因为包括命令本身
        if msg.from_user and msg.from_user.id == client.me.id:  # 删除自己的发言
            try:
                await msg.delete()
                deleted_count += 1
                if deleted_count > count:
                    break
            except Exception:
                continue
        elif msg.chat.type in ["channel"] and msg.sender_chat and msg.sender_chat.id in client.MY_CHANNEL_IDS:  # 删除指定频道的发言
            try:
                await msg.delete()
                deleted_count += 1
                if deleted_count > count:
                    break
            except Exception:
                continue

    # 发送完成消息
    completion_msg = await client.send_message(
        chat_id,
        f"已经完成删除指令，删除了 {deleted_count - 1} 条留言"  # -1 因为不计入命令本身
    )

    # 等待1秒后删除完成消息
    await asyncio.sleep(1)
    await completion_msg.delete()