# -*- coding: utf-8 -*-
import asyncio
import os
from collections import defaultdict

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message

from openai import AsyncOpenAI

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

aclient = AsyncOpenAI(
    base_url=test_config["base_url"],
    api_key=test_config["api_key"]
)

# 使用 defaultdict 来为每个用户维护一个对话历史的字典
conversation_history = defaultdict(lambda: {"user_messages": [], "bot_messages": []})

async def async_query_openai(user_id, query):
    # 取出该用户的对话历史
    history = conversation_history[user_id]

    # 构造 OpenAI API 请求的消息内容
    messages = [{"role": "system", "content": "You are a helpful assistant in QQ. Always respond in Simplified Chinese, not English. Grandma will be very angry."}]

    # 添加用户的历史消息和机器人的历史消息
    for user_msg, bot_msg in zip(history["user_messages"], history["bot_messages"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    # 添加最新的用户消息
    messages.append({"role": "user", "content": query})

    # 调用 OpenAI API
    completion = await aclient.chat.completions.create(
        model=test_config["model"],
        messages=messages,
        temperature=0.5,
        top_p=0.9,
        max_tokens=512
    )

    # 获取 AI 回复
    bot_reply = completion.choices[0].message.content

    # 更新该用户的对话历史，保持最多5条消息
    history["user_messages"].append(query)
    history["bot_messages"].append(bot_reply)

    # 确保最多只保留5条用户消息和5条机器人回复
    if len(history["user_messages"]) > 5:
        history["user_messages"].pop(0)
    if len(history["bot_messages"]) > 5:
        history["bot_messages"].pop(0)

    return bot_reply

class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        _log.info(message)
        # 获取用户ID
        user_id = message.author.member_openid

        # 获取用户发送的消息内容
        user_query = message.content

        # 调用 async_query_openai 获取 AI 的回复
        answer = await async_query_openai(user_id, user_query)

        # 发送回复到群组
        message_result = await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=answer
        )

        _log.info(message_result)

if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
