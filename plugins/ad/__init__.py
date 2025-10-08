import asyncio
import re
import httpx
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message

async def extract_torrent_name_from_html(tid: str) -> str:
    """从HTML页面中提取种子名称"""
    try:
        # 设置Cookie
        cookies = {
            "c_secure_login": "bm9wZQ%3D%3D",
            "c_secure_pass": "6c4659fad2bc2933c3c3bd6b3b05b755",
            "c_secure_uid": "MTczMTg%3D"
        }
        
        # 发送GET请求获取页面内容
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://audiences.me/details.php?id={tid}",
                cookies=cookies,
                timeout=30.0
            )
            
            if response.status_code == 200:
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('title')
                
                if title_tag and title_tag.string:
                    # 提取种子名称
                    title_content = title_tag.string
                    # 匹配双引号中的内容
                    match = re.search(r'"([^"]+)"', title_content)
                    if match:
                        return match.group(1)
            
            return f"id={tid}"
    except Exception as e:
        print(f"提取种子名称时出错: {str(e)}")
        return f"id={tid}"

async def process_ad_request_generic(client: Client, message: Message, tid: str, is_free: bool):
    """处理 ad free 和 ad top 命令的通用函数"""
    
    # 根据类型准备POST数据
    if is_free:
        data = {
            "tid": tid,
            "promoteTime": "24",
            "promoteType": "2"
        }
    else:
        data = {
            "tid": tid,
            "upTime": "24",
            "upBonus": "1"
        }
    
    # 设置Cookie
    cookies = {
        "c_secure_login": "bm9wZQ%3D%3D",
        "c_secure_pass": "6c4659fad2bc2933c3c3bd6b3b05b755",
        "c_secure_uid": "MTczMTg%3D"
    }
    
    # 发送POST请求
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://audiences.me/promote.php",
                data=data,
                cookies=cookies,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return True, tid
            else:
                return False, f"促销种子失败: 状态码 {response.status_code}"
                
    except Exception as e:
        return False, f"请求出错: {str(e)}"

async def process_ad_free_request(client: Client, message: Message, tid: str):
    """处理 ad free 命令，发送POST请求到 promote.php"""
    return await process_ad_request_generic(client, message, tid, True)

async def process_ad_top_request(client: Client, message: Message, tid: str):
    """处理 ad top 命令，发送POST请求"""
    return await process_ad_request_generic(client, message, tid, False)

async def process_ad_request(client: Client, message: Message):
    """处理 ad 命令，根据参数调用相应的处理函数"""
    
    # 获取命令文本
    command_text = message.text.strip()
    
    # 使用正则表达式匹配 'ad tid' 格式，支持多个tid或URL
    # 支持中英文逗号
    pattern = r'^[,，]ad\s+(.+)$'
    match = re.match(pattern, command_text)
    
    if match:
        # 提取所有参数
        params = match.group(1).strip()
        
        # 分割参数，支持空格分隔
        items = params.split()
        tids = []
        
        # 处理每个参数，可能是tid或URL
        for item in items:
            # 如果是URL，提取tid
            url_pattern = r'https://audiences\.me/details\.php\?id=(\d+)'
            url_match = re.match(url_pattern, item)
            if url_match:
                tids.append(url_match.group(1))
            # 如果是纯数字，直接添加
            elif item.isdigit() and len(item) == 6:
                tids.append(item)
        
        # 如果找到了有效的tid
        if tids:
            # 收集所有操作结果
            results = []
            
            # 对每个tid先执行top操作，再执行free操作
            for tid in tids:
                try:
                    # 先执行top操作
                    top_success, top_result = await process_ad_top_request(client, message, tid)
                    if not top_success:
                        # 如果top操作失败，记录错误但继续处理free操作
                        print(f"处理tid {tid} 的top操作时出错: {top_result}")
                    
                    # 再执行free操作
                    free_success, free_result = await process_ad_free_request(client, message, tid)
                    if free_success:
                        results.append(free_result)
                    else:
                        # 如果free操作失败，记录错误
                        print(f"处理tid {tid} 的free操作时出错: {free_result}")
                except Exception as e:
                    # 如果某个操作失败，记录错误但继续处理其他tid
                    print(f"处理tid {tid} 时出错: {str(e)}")
            
            # 统一编辑消息
            if results:
                # 构建成功消息
                success_lines = [f"成功置顶促销{len(results)}个种子"]
                for tid in results:
                    # 获取种子名称
                    torrent_name = await extract_torrent_name_from_html(tid)
                    success_lines.append(f"[{torrent_name}](https://audiences.me/details.php?id={tid})")
                success_message = "\n".join(success_lines)
                await client.edit_message_text(message.chat.id, message.id, success_message)
            
            return True
    
    # 如果格式不匹配，返回False表示未处理
    return False

# 注册消息处理器
@Client.on_message(filters.text & ~filters.command([]))
async def handle_ad_messages(client: Client, message: Message):
    """处理文本消息，检查是否为ad命令"""
    # 检查是否为ad命令格式
    if message.text and (message.text.startswith(',') or message.text.startswith('，')):
        if 'ad' in message.text:
            # 尝试处理ad请求
            processed = await process_ad_request(client, message)
            if processed:
                return
    
    # 如果不是ad命令或其他处理逻辑，可以在这里添加
    pass