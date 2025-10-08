from pyrogram import Client, filters
import asyncio
from openai import OpenAI
import os
import base64
import httpx
from config_loader import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

# 初始化 DeepSeek 客户端
if DEEPSEEK_API_KEY is None or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
    raise ValueError("DEEPSEEK_API_KEY environment variable is required")
    
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# 用于存储对话历史的字典，按 chat_id 分组
conversation_history = {}

async def download_media(client, message):
    """下载媒体文件并返回文件路径"""
    if message.photo:
        file_path = await client.download_media(message.photo.file_id)
        return file_path
    elif message.sticker:
        file_path = await client.download_media(message.sticker.file_id)
        return file_path
    return None

def encode_image_to_base64(image_path):
    """将图片编码为base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def process_deepseek_request(client, message):
    """处理 DeepSeek 请求：文本生成"""
    chat_id = message.chat.id
    reply = message.reply_to_message
    command_text = message.text.split("，ds", 1)[1].strip() if message.text and "，ds" in message.text else ""

    if message.text and ("，ds" in message.text or ",ds" in message.text):
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message.id,
            text="思考中"
        )

    if chat_id not in conversation_history:
        conversation_history[chat_id] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # 处理图片或sticker
    if message.photo or message.sticker:
        # 下载媒体文件
        media_path = await download_media(client, message)
        if media_path:
            # 将图片编码为base64
            base64_image = encode_image_to_base64(media_path)
            # 添加到对话历史
            conversation_history[chat_id].append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            })
            # 清理下载的文件
            os.remove(media_path)
            response = await process_multimodal_text(chat_id)
        else:
            response = "处理媒体文件时出错"
    elif command_text:
        conversation_history[chat_id].append({"role": "user", "content": command_text})
        response = await process_multimodal_text(chat_id)
    elif reply:
        if reply.photo or reply.sticker:
            # 处理回复的媒体消息
            media_path = await download_media(client, reply)
            if media_path:
                base64_image = encode_image_to_base64(media_path)
                conversation_history[chat_id].append({
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                })
                # 如果有文本指令，也添加到内容中
                if command_text:
                    conversation_history[chat_id][-1]["content"].append({
                        "type": "text",
                        "text": command_text
                    })
                os.remove(media_path)
                response = await process_multimodal_text(chat_id)
            else:
                response = "处理媒体文件时出错"
        elif reply.text:
            conversation_history[chat_id].append({"role": "user", "content": reply.text})
            response = await process_multimodal_text(chat_id)
        else:
            response = "请直接输入文本（，ds 文本）或回复消息/图片/sticker！"
    else:
        response = "请直接输入文本（，ds 文本）或发送/回复图片/sticker！"

    if message.text and ("，ds" in message.text or ",ds" in message.text):
        response = response[:4096] if len(response) > 4096 else response
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message.id,
            text=response
        )
    else:
        await client.send_message(chat_id, response)

async def process_multimodal_text(chat_id):
    """处理多模态文本，带上下文"""
    try:
        response = deepseek_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=conversation_history[chat_id],
            max_tokens=1000
        )
        result = response.choices[0].message.content.strip()
        conversation_history[chat_id].append({"role": "assistant", "content": result})
        if len(conversation_history[chat_id]) > 10:
            conversation_history[chat_id] = conversation_history[chat_id][-10:]
        return result
    except Exception as e:
        return f"处理文本时出错：{str(e)}"