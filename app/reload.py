import asyncio
import importlib
import os
import sys
from pyrogram import Client
from pyrogram.types import Message


async def process_reload_request(client: Client, message: Message):
    """处理 reload 命令，重新加载 plugins 目录下的插件"""
    sent_message = await message.edit_text("正在重新加载插件...")
    
    try:
        # 重新加载插件
        reload_plugins()
        await sent_message.edit_text("插件重新加载完成！")
        print("插件重新加载完成")
    except Exception as e:
        error_msg = f"重新加载插件时出错: {str(e)}"
        await sent_message.edit_text(error_msg)
        print(error_msg)
    
    # 等待2秒后删除消息
    await asyncio.sleep(2)
    await message.delete()
    await sent_message.delete()


def reload_plugins():
    """重新加载 plugins 目录下的所有插件"""
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        print(f"插件目录 {plugins_dir} 不存在")
        return
    
    # 遍历插件目录下的所有文件和文件夹
    for item in os.listdir(plugins_dir):
        item_path = os.path.join(plugins_dir, item)
        # 如果是目录，则认为是一个插件
        if os.path.isdir(item_path) and item != "__pycache__":
            plugin_name = item
            module_name = f"plugins.{plugin_name}"
            try:
                # 如果模块已加载，则重新加载
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    print(f"重新加载插件: {plugin_name}")
                else:
                    # 首次加载
                    importlib.import_module(module_name)
                    print(f"加载插件: {plugin_name}")
            except Exception as e:
                print(f"重新加载插件 {plugin_name} 失败: {str(e)}")
        # 如果是.py文件，也保持兼容性
        elif item.endswith(".py") and item != "__init__.py":
            plugin_name = item[:-3]
            module_name = f"plugins.{plugin_name}"
            try:
                # 如果模块已加载，则重新加载
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    print(f"重新加载插件: {plugin_name}")
                else:
                    # 首次加载
                    importlib.import_module(module_name)
                    print(f"加载插件: {plugin_name}")
            except Exception as e:
                print(f"重新加载插件 {plugin_name} 失败: {str(e)}")