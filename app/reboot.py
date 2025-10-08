import asyncio
import os
import sys
from pyrogram import Client
from pyrogram.types import Message


async def process_reboot_request(client: Client, message: Message):
    """处理 reboot 命令，重启 bot.py"""
    sent_message = await message.edit_text("正在重启机器人...")
    await message.delete()  # 删除用户命令消息

    # 等待1秒以确保消息发送完成
    await asyncio.sleep(1)
    await sent_message.delete()  # 这行不会执行，仅作示例
    # 重启 bot.py
    # 使用 os.execv 替换当前进程，重新执行 sys.argv[0]（即 bot.py）
    os.execv(sys.executable, [sys.executable] + sys.argv)

    # 注意：os.execv 会替换当前进程，后续代码不会执行
    # 如果需要清理，可以在 execv 之前执行
