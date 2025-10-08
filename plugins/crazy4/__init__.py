import asyncio
import json
import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

async def process_crazy4_request(client: Client, message: Message):
    """处理 crazy4 命令，从API获取内容并回复"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://kfc-crazy-thursday.vercel.app/api/index") as response:
                if response.status == 200:
                    data = await response.text()
                    await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message.id,
                        text=data,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message.id,
                        text="获取内容失败，请稍后再试",
                        parse_mode=ParseMode.MARKDOWN
                    )
    except Exception as e:
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=f"发生错误: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )
