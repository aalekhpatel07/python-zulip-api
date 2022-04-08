#!/usr/bin/python3

from typing import Dict, Union
import logging
import openai
import random

from requests.exceptions import ConnectionError, HTTPError
from zulip_bots.lib import BotHandler


class MarvHandler:
    """
    This plugin allows users to talk to Marv (creation of OpenAI),
    a sassy chatbot.
    The bot looks for messages starting with @mention of the bot
    and responds with an appropriate.
    It also responds to private messages.
    """

    def usage(self) -> str:
        return """
            This plugin allows users to converse with the sassy Marv chatbot
            by OpenAI. Users should preface the question with the Marv-bot @mention.
            The bot responds also to private messages.
            """

    def initialize(self, bot_handler: BotHandler) -> None:
        self.config_info = bot_handler.get_config_info("marv")

    def handle_message(self, message: Dict[str, str], bot_handler: BotHandler) -> None:
        bot_response = get_bot_marv_response(message, bot_handler, self.config_info)
        bot_handler.send_reply(message, bot_response)


class MarvNoResponseException(Exception):
    pass


def get_openAI_marv_response(question: str, api_key: str = None, prompt: str = None) -> str:

    if prompt is None:
        prompt = f"Marv is a chatbot that reluctantly answers questions with sarcastic responses:\n\nYou: How many pounds are in a kilogram?\nMarv: This again? There are 2.2 pounds in a kilogram. Please make a note of this.\nYou: What does HTML stand for?\nMarv: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.\nYou: When did the first airplane fly?\nMarv: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.\nYou: What is the meaning of life?\nMarv: I’m not sure. I’ll ask my friend Google.\nYou: {question}?\nMarv:"

    openai.api_key = api_key
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=prompt,
      temperature=0.5,
      max_tokens=60,
      top_p=0.3,
      frequency_penalty=0.5,
      presence_penalty=0.0
    )
    if "choices" in response and len(response["choices"]) > 0:
        return random.choice(response["choices"])["text"]
    raise MarvNoResponseException()


def get_bot_marv_response(
    message: Dict[str, str], bot_handler: BotHandler, config_info: Dict[str, str]
) -> str:
    keyword = message["content"]
    try:
        data = get_openAI_marv_response(question=keyword, api_key=config_info["key"])
        return data
    except requests.exceptions.ConnectionError:
        return (
            "Uh oh, sorry :slightly_frowning_face:, I "
            "cannot process your request right now. But, "
            "let's try again later! :grin:"
        )
    except MarvNoResponseException:
        return 'Sorry, I don\'t even know what to say abot "%s"! ' ":astonished:" % (keyword,)


handler_class = MarvHandler

