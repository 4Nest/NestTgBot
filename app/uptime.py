from pyrogram import Client, filters
import time
import asyncio  # 确保引入 asyncio
from datetime import timedelta

# 记录启动时间
start_time = time.time()

async def show_uptime(client, message):
    """显示机器人运行时长"""
    current_time = time.time()
    uptime_seconds = current_time - start_time

    # 自定义格式化
    days = int(uptime_seconds // (24 * 3600))
    uptime_seconds %= (24 * 3600)
    hours = int(uptime_seconds // 3600)
    uptime_seconds %= 3600
    minutes = int(uptime_seconds // 60)
    seconds = int(uptime_seconds % 60)

    if days > 0:
        uptime_str = f"{days} 天 {hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # 机器人回复消息，并保存返回的消息对象
    sent_message = await message.reply(f"🤖机器人已运行: {uptime_str}")

    # 删除用户的命令消息
    await message.delete()

    # 等待 1 秒后删除机器人刚刚发送的消息
    await asyncio.sleep(1)
    await sent_message.delete()