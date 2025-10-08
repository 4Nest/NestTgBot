from pyrogram import Client, filters
import asyncio
from openai import OpenAI
import base64
import os
from PIL import Image
import subprocess
import gzip

# Try to import magic, with fallback for Windows
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    magic = None
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. Some file type detection features may be limited.")

from rlottie_python import LottieAnimation
from config_loader import XAI_API_KEY, XAI_BASE_URL

# 初始化 xAI 客户端
xai_client = OpenAI(
    api_key=XAI_API_KEY,
    base_url=XAI_BASE_URL,
)

# 用于存储对话历史的字典，按 chat_id 分组
conversation_history = {}

# 检查是否为 TGS 文件
def is_tgs_file(file_path):
    try:
        with gzip.open(file_path, 'rb') as f:
            f.read(1)
        return True
    except (OSError, gzip.BadGzipFile):
        return False

# 检测文件 MIME 类型
def get_file_mime_type(file_path):
    # Check if magic is available
    if not MAGIC_AVAILABLE or magic is None:
        # Fallback to file extension-based detection
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type
        except Exception:
            return None
    
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        return mime_type
    except Exception:
        return None

async def process_xai_request(client, message):
    """处理 xAI 请求：文本生成或图像识别"""
    chat_id = message.chat.id
    reply = message.reply_to_message
    command_text = message.text.split("，xai", 1)[1].strip() if message.text and "，xai" in message.text else ""

    if message.text and "，xai" in message.text:
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message.id,
            text="思考中"
        )

    image_path = None
    if reply and (reply.photo or reply.sticker):
        media = reply.photo or reply.sticker
        image_path = await client.download_media(media.file_id)
    elif message.photo or message.sticker:
        media = message.photo or message.sticker
        image_path = await client.download_media(media.file_id)

    if chat_id not in conversation_history:
        conversation_history[chat_id] = [
            {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."}
        ]

    if image_path:
        response = await process_image(image_path, chat_id)
        if os.path.exists(image_path):
            os.remove(image_path)
    elif command_text:
        conversation_history[chat_id].append({"role": "user", "content": command_text})
        response = await process_text(chat_id)
    elif reply and reply.text:
        conversation_history[chat_id].append({"role": "user", "content": reply.text})
        response = await process_text(chat_id)
    else:
        response = "请直接输入文本（，xai 文本）、回复消息或发送图片/贴图！"

    if message.text and "，xai" in message.text:
        response = response[:4096] if len(response) > 4096 else response
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message.id,
            text=response
        )
    else:
        await client.send_message(chat_id, response)

async def process_text(chat_id):
    """处理文本，带上下文，使用 grok-2-1212 模型"""
    try:
        # 过滤掉包含图片的对话历史，仅保留文本消息
        text_only_history = [
            msg for msg in conversation_history[chat_id]
            if isinstance(msg["content"], str)  # 只保留纯文本消息
        ]
        response = xai_client.chat.completions.create(
            model="grok-2-1212",
            messages=text_only_history,
            max_tokens=500
        )
        result = response.choices[0].message.content.strip()
        conversation_history[chat_id].append({"role": "assistant", "content": result})
        if len(conversation_history[chat_id]) > 10:
            conversation_history[chat_id] = conversation_history[chat_id][-10:]
        return result
    except Exception as e:
        return f"处理文本时出错：{str(e)}"

async def process_image(image_path, chat_id):
    """处理图片，使用 grok-2-vision-1212 模型"""
    try:
        file_ext = os.path.splitext(image_path)[1].lower()
        mime_type = get_file_mime_type(image_path)

        if file_ext in {".png", ".jpg", ".jpeg"} and mime_type in {"image/png", "image/jpeg"}:
            pass
        else:
            png_path = image_path.replace(file_ext, ".png")
            if file_ext == ".tgs" or is_tgs_file(image_path):
                try:
                    anim = LottieAnimation.from_tgs(image_path)
                    anim.save_frame(png_path, frame_num=0)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    image_path = png_path
                except Exception as e:
                    return f"TGS 文件转换失败：{str(e)}"
            elif file_ext == ".webp" and mime_type and "image/webp" in mime_type:
                try:
                    with Image.open(image_path) as img:
                        img.convert("RGBA").save(png_path, "PNG")
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    image_path = png_path
                except Exception:
                    try:
                        subprocess.run(
                            ["ffmpeg", "-i", image_path, "-vf", "scale=320:-1", "-vframes", "1", "-y", png_path],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        image_path = png_path
                    except subprocess.CalledProcessError as e:
                        return f"ffmpeg 转换 WEBP 文件失败：{e.stderr}"
            elif mime_type and "video/webm" in mime_type:
                try:
                    subprocess.run(
                        ["ffmpeg", "-i", image_path, "-vf", "scale=320:-1", "-vframes", "1", "-y", png_path],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    image_path = png_path
                except subprocess.CalledProcessError as e:
                    return f"ffmpeg 转换 WEBM 文件失败：{e.stderr}"
            else:
                return f"不支持的文件格式：{file_ext}，MIME 类型：{mime_type}"

        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            return f"转换后的文件无效：{image_path}, 大小：{os.path.getsize(image_path)} 字节"

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        image_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "请描述这张图片的内容"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
            ],
        }
        conversation_history[chat_id].append(image_message)

        response = xai_client.chat.completions.create(
            model="grok-2-vision-1212",
            messages=conversation_history[chat_id],
            max_tokens=500
        )
        result = response.choices[0].message.content.strip()
        conversation_history[chat_id].append({"role": "assistant", "content": result})
        if len(conversation_history[chat_id]) > 10:
            conversation_history[chat_id] = conversation_history[chat_id][-10:]
        return result
    except Exception as e:
        return f"处理图片时出错：{str(e)}"