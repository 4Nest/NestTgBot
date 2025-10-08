import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# 数据文件路径
DATA_FILE = "say_data.json"

# 加载初始数据
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 处理可能存在的转义字符
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.replace("\\n", "\n")
            return data
    return {
        "86": "[解除 Telegram 无法主动发起私聊/私聊限制 的办法](https://t.me/tgcnz/480)",
        "ask": "[提问的智慧](https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md)",
        "words": "[如何自己写识别词](https://github.com/4Nest/MoviePilot-Settings/blob/main/V2/readme.md#%E5%A6%82%E4%BD%95%E8%87%AA%E5%B7%B1%E5%86%99%E8%AF%86%E5%88%AB%E8%AF%8D)\n\n现成词表:\n[布丁词表](https://github.com/Putarku/MoviePilot-Help/tree/main/Words)\n[NEST词表](https://github.com/4Nest/MoviePilot-Settings/blob/main/Words/anime.txt)  [(搭配使用)](https://github.com/4Nest/MoviePilot-Settings/blob/main/V2/readme.md)",
        "rules": "[V2规则参考](https://t.me/fakenest/7)",
        "rename": "[重命名参考](https://t.me/fakenest/8)",
        "githubtoken": "[Github Token获取](https://t.me/MoviePilot_Wiki/20)",
        "v1tov2": "V1迁移V2插件\n[迁移订阅 - boeto](https://github.com/boeto/MoviePilot-Plugins)\n[历史记录迁移 - 官方插件](https://github.com/jxxghp/MoviePilot-Plugins)",
        "v2": "[MoviePilotV2使用教程](https://blog.2nest.top/article/mpv2)",
        "nat": "[打洞王教程](https://flowus.cn/wangdefa/share/87ea8216-b6b4-4f18-9f3d-81bd5c872f24?code=572YLM)",
        "wechat": "[企业微信机器人配置教程 MoviePilot-v2](https://t.me/MoviePilot_Wiki/36)",
        "mteam": "[馒头添加教程 For MoviePilot-v2](https://t.me/MoviePilot_Wiki/39)",
        "fnv2": "[fnOS部署V2](https://t.me/MoviePilot_Wiki/35)",
        "smbox": "[SMBox部署](https://smbox.buzheteng.org/guide/)\n[SMBox交流群](https://t.me/buaizheteng)\n[SMBoxBot](https://t.me/sm_licence_bot)",
        "cf": "[使用CF自选IP解决Tracker未工作及网站访问缓慢](https://wiki.m-team.cc/zh-tw/cf-choose-better-ip)",
        "ad": "[Moviepilot Audiences Words](https://t.me/fakenest/14)\n观众资源识别词词表"
    }

# 保存数据到文件
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def process_say_request(client: Client, message: Message):
    """处理 say 命令，返回预定义的响应或执行添加/删除/编辑操作"""
    # 加载当前数据
    response_dict = load_data()

    # 从 message.command 获取参数
    if len(message.command) > 1:
        subcommand = message.command[1].lower().strip()
    else:
        subcommand = ""

    if subcommand == "list":
        if response_dict:
            response_lines = []
            for key, value in response_dict.items():
                truncated_value = (value[:20] + "...") if len(value) > 20 else value
                response_lines.append(f"{key}: {truncated_value}")
            response = "\n".join(response_lines)
        else:
            response = "当前没有内容"
        edit = await client.edit_message_text(message.chat.id, message.id, response, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await edit.delete()
    elif subcommand == "add" and len(message.command) >= 4:
        key = message.command[2].strip()
        value = " ".join(message.command[3:]).strip()
        # 处理换行符转义
        value = value.replace("\\n", "\n")
        if key in response_dict:
            response = f"键 '{key}' 已存在，无法重复添加"
        else:
            response_dict[key] = value
            save_data(response_dict)
            response = f"成功添加: {key} -> {value}"
        edit = await client.edit_message_text(message.chat.id, message.id, response, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await edit.delete()
    elif subcommand == "remove" and len(message.command) >= 3:
        key = message.command[2].strip()
        if key in response_dict:
            del response_dict[key]
            save_data(response_dict)
            response = f"成功删除: {key}"
        else:
            response = f"键 '{key}' 不存在，无法删除"
        edit = await client.edit_message_text(message.chat.id, message.id, response, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await edit.delete()
    elif subcommand == "edit" and len(message.command) >= 4:
        key = message.command[2].strip()
        new_value = " ".join(message.command[3:]).strip()
        # 处理换行符转义
        new_value = new_value.replace("\\n", "\n")
        if key in response_dict:
            response_dict[key] = new_value
            save_data(response_dict)
            response = f"成功修改: {key} -> {new_value}"
        else:
            response = f"键 '{key}' 不存在，无法修改"
        edit = await client.edit_message_text(message.chat.id, message.id, response, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await edit.delete()
    elif subcommand == "all":
        response = "\n".join(response_dict.keys())
        edit = await client.edit_message_text(message.chat.id, message.id, response, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await edit.delete()
    else:
        # 查询已有内容
        key = subcommand if subcommand else ""
        response = response_dict.get(key, "Invalid command")
        edit = await client.edit_message_text(message.chat.id, message.id, response, parse_mode=ParseMode.MARKDOWN)
        if response == "Invalid command":
            await asyncio.sleep(1)
            await edit.delete()
