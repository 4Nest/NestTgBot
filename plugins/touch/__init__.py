import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message

async def process_touch_request(client: Client, message: Message):
    """处理 touch 命令，根据指定物品获取，若无指定则随机"""
    items = [
        "胖次", "小裙裙", "嗨丝", "白丝", "CPU", "硬盘", "电源线", "NAS", "内存条", "显卡", "键盘", "鼠标",
        "路由器", "交换机", "网线", "UPS", "显示器", "主板", "散热器", "机箱", "SSD", "机械键盘",
        "鼠标垫", "耳机", "音响", "摄像头", "麦克风", "充电器", "数据线", "U盘", "移动硬盘", "VR眼镜",
        "智能手表", "平板电脑", "游戏机", "蓝牙耳机", "无线充电器", "智能音箱", "数码相机", "打印机", "扫描仪", "投影仪"
    ]
    msg = message.reply_to_message
    command_text = message.text.strip()  # 获取命令全文并去除首尾空格

    # 判断是否有指定物品
    if len(command_text.split()) > 1:  # 如果命令包含多个词
        target_item = command_text.split()[1]  # 直接取第二个词作为目标物品
    else:
        target_item = random.choice(items)  # 没有指定物品时随机选择

    # 直接编辑原消息
    await message.edit_text("正在获取...")
    await asyncio.sleep(3)  # 等待3秒

    if msg and msg.from_user:
        user = msg.from_user
        if user.id == 5929966071:
            response = "下水道老鼠，恶心"
            try:
                await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=response)  # 编辑消息内容
            except Exception as e:
                print(f"编辑消息失败: {e}")
                await message.delete()  # 删除消息
        elif user.id == 1914680102:
            response = "摸到二次元了，一刀砍死二次元"
            try:
                await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=response)  # 编辑消息内容
            except Exception as e:
                print(f"编辑消息失败: {e}")
                await message.delete()  # 删除消息
        elif user.username:
            response = f"成功获得**{user.username}**的**{target_item}**"
            try:
                await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=response)  # 编辑消息内容
            except Exception as e:
                print(f"编辑消息失败: {e}")
                await message.delete()  # 删除消息
        else:
            response = f"成功获得**None**的**{target_item}**"
            try:
                await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=response)  # 编辑消息内容
            except Exception as e:
                print(f"编辑消息失败: {e}")
                await message.delete()  # 删除消息
    elif msg and msg.sender_chat:
        chat = msg.sender_chat
        response = f"成功获得**{chat.title}**的**{target_item}**"
        try:
            await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=response)  # 编辑消息内容
        except Exception as e:
            print(f"编辑消息失败: {e}")
            await message.delete()  # 删除消息
    else:
        try:
            await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text="获取失败：请回复一条消息以获取物品")  # 编辑消息内容
        except Exception as e:
            print(f"编辑消息失败: {e}")
        await asyncio.sleep(1)  # 失败时显示1秒
        await message.delete()  # 删除消息