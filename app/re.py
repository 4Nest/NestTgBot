from pyrogram import Client, filters


async def reply_forward(client, message):
    """ 当用户在回复消息时输入 re [数字]，机器人会根据数字转发被回复的消息对应次数，默认1次 """
    replied_message = message.reply_to_message  # 获取被回复的消息
    chat_id = message.chat.id  # 获取当前对话 ID

    # 获取命令参数
    args = message.text.split()
    # 默认重复次数为1
    repeat_count = 1

    # 如果有参数且是数字，设置为重复次数
    if len(args) > 1 and args[1].isdigit():
        repeat_count = int(args[1])

    if replied_message:
        # 根据指定次数重复转发
        for _ in range(repeat_count):
            await replied_message.forward(chat_id)
        await message.delete()  # 删除re指令
    else:
        await message.reply("")