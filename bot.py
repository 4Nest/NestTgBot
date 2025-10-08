import os
import importlib
from pyrogram import Client, filters
from config_loader import API_ID, API_HASH, MY_USER_ID, MY_CHANNEL_IDS

# 检查是否为空并转换为正确类型
if API_ID is None or API_HASH is None or MY_USER_ID is None:
    raise ValueError("API_ID, API_HASH, and MY_USER_ID must be set in config.yaml")
api_id = int(API_ID)
MY_USER_ID = int(MY_USER_ID)

# 处理 MY_CHANNEL_IDS，转换为整数列表
if MY_CHANNEL_IDS:
    try:
        cleaned_ids = MY_CHANNEL_IDS.strip().strip('"').split(",")
        MY_CHANNEL_IDS = [int(chat_id.strip()) for chat_id in cleaned_ids if chat_id.strip()]
    except ValueError as e:
        print(f"警告：频道ID格式错误: {e}")
        MY_CHANNEL_IDS = []
else:
    MY_CHANNEL_IDS = []
    print("MY_CHANNEL_IDS 未设置")

# 设置 session 文件路径以实现持久化
session_dir = "/app/data"  # Docker 中的默认路径
# 如果在本地运行且不存在 /app/data 目录，则使用当前目录下的 data 目录
if not os.path.exists("/app/data"):
    session_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(session_dir, exist_ok=True)

session_file = os.path.join(session_dir, "my_bot.session")

# 创建实例
app = Client(session_file, api_id=api_id, api_hash=API_HASH)

# 固定的 app 模块处理器
fixed_handlers = {
    "re": ("app.re", "reply_forward", filters.reply),  # 需要回复消息
    "dme": ("app.dme", "delete_messages"),
    "uptime": ("app.uptime", "show_uptime"),
    "reboot": ("app.reboot", "process_reboot_request"),
    "info": ("app.info", "process_info_request"),
    "reload": ("app.reload", "process_reload_request"),
    "xai": ("app.xai", "process_xai_request"),
    "ds": ("app.deepseek", "process_deepseek_request"),
}

# 创建自定义过滤器，支持 MY_USER_ID 和 MY_CHANNEL_IDS
def authorized_user():
    async def func(flt, client, message):
        # 检查是否来自授权用户
        if message.from_user and message.from_user.id == MY_USER_ID:
            return True
        # 检查是否来自授权频道
        if message.sender_chat and message.sender_chat.id in MY_CHANNEL_IDS:
            return True
        return False
    return filters.create(func)

# 动态加载 plugins 目录下的插件
def load_plugins():
    plugins_dir = "plugins"
    loaded_plugins = []  # 记录成功加载的插件
    failed_plugins = []  # 记录加载失败的插件
    
    if not os.path.exists(plugins_dir):
        print(f"插件目录 {plugins_dir} 不存在，跳过加载")
        return
    
    print("开始加载插件...")
    
    # 遍历插件目录下的所有文件和文件夹
    for item in os.listdir(plugins_dir):
        item_path = os.path.join(plugins_dir, item)
        # 如果是目录，则认为是一个插件
        if os.path.isdir(item_path):
            plugin_name = item
            module_name = f"plugins.{plugin_name}"
            try:
                # 尝试导入插件模块
                module = importlib.import_module(module_name)
                handler_func_name = f"process_{plugin_name}_request"
                if hasattr(module, handler_func_name):
                    handler_func = getattr(module, handler_func_name)
                    # 注册插件命令
                    @app.on_message(filters.command(plugin_name, prefixes=["，", ","]) & authorized_user())
                    async def dynamic_handler(client, message, func=handler_func):
                        print(f"触发插件: {plugin_name}, chat_id={message.chat.id}, from_user={message.from_user.id if message.from_user else '匿名'}, text={message.text}")
                        await func(client, message)
                    loaded_plugins.append(plugin_name)
                    print(f"✓ 成功加载插件: {plugin_name}")
                else:
                    failed_plugins.append(plugin_name)
                    print(f"✗ 插件 {plugin_name} 未定义 {handler_func_name} 函数，跳过加载")
            except Exception as e:
                failed_plugins.append(plugin_name)
                print(f"✗ 加载插件 {plugin_name} 失败: {str(e)}")
        # 如果是.py文件，也保持兼容性
        elif item.endswith(".py") and item != "__init__.py":
            plugin_name = item[:-3]
            module_name = f"plugins.{plugin_name}"
            try:
                module = importlib.import_module(module_name)
                handler_func_name = f"process_{plugin_name}_request"
                if hasattr(module, handler_func_name):
                    handler_func = getattr(module, handler_func_name)
                    # 注册插件命令
                    @app.on_message(filters.command(plugin_name, prefixes=["，", ","]) & authorized_user())
                    async def dynamic_handler(client, message, func=handler_func):
                        print(f"触发插件: {plugin_name}, chat_id={message.chat.id}, from_user={message.from_user.id if message.from_user else '匿名'}, text={message.text}")
                        await func(client, message)
                    loaded_plugins.append(plugin_name)
                    print(f"✓ 成功加载插件: {plugin_name}")
                else:
                    failed_plugins.append(plugin_name)
                    print(f"✗ 插件 {plugin_name} 未定义 {handler_func_name} 函数，跳过加载")
            except Exception as e:
                failed_plugins.append(plugin_name)
                print(f"✗ 加载插件 {plugin_name} 失败: {str(e)}")
    
    # 显示加载总结
    print(f"插件加载完成。成功: {len(loaded_plugins)} 个, 失败: {len(failed_plugins)} 个")
    if loaded_plugins:
        print(f"已加载插件: {', '.join(loaded_plugins)}")
    if failed_plugins:
        print(f"加载失败插件: {', '.join(failed_plugins)}")

# 注册固定的 app 处理器
for command, info in fixed_handlers.items():
    module_name = info[0]
    func_name = info[1]
    extra_filter = info[2] if len(info) > 2 else None
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        filter_ = filters.command(command, prefixes=["，", ","]) & authorized_user()
        if extra_filter:
            filter_ &= extra_filter
        @app.on_message(filter_)
        async def fixed_handler(client, message, f=func):
            print(f"触发命令: {command}, chat_id={message.chat.id}, from_user={message.from_user.id if message.from_user else '匿名'}, text={message.text}")
            await f(client, message)
    except Exception as e:
        print(f"加载固定模块 {command} 失败: {str(e)}")

# 先加载插件
load_plugins()

# 注册 record 插件的消息监听器，支持所有聊天类型
try:
    from plugins.record import log_chat_messages
    @app.on_message()
    async def global_message_handler(client, message):
        # print(f"收到消息: chat_id={message.chat.id}, text={message.text or '无文本'}")
        await log_chat_messages(client, message)
except ImportError:
    print("警告: record 插件未找到，消息记录功能将不可用")
    # 注册一个空的处理器以避免错误
    @app.on_message()
    async def global_message_handler(client, message):
        pass

# 运行机器人
app.run()