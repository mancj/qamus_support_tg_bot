from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.bot.utils import ChatGPTService, load_knowledge_base
from app.config import Config


class ChatGPTMiddleware(BaseMiddleware):
    """
    Middleware for integrating ChatGPT service with Aiogram.

    Args:
        config (Config): The application configuration.
    """

    def __init__(self, config: Config) -> None:
        """
        Initializes the ChatGPTMiddleware instance.

        :param config: The application configuration.
        """
        self.chatgpt_service = ChatGPTService(config.openai)

        # Load knowledge base
        knowledge_base = load_knowledge_base(config.openai.KNOWLEDGE_BASE_PATH)
        self.chatgpt_service.set_knowledge_base(knowledge_base)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Call the middleware.

        :param handler: The handler function.
        :param event: The Telegram event.
        :param data: Additional data.
        :return: The result of the handler function.
        """
        # Add chatgpt_service to data for use in subsequent handlers
        data["chatgpt_service"] = self.chatgpt_service

        # Call the handler function with the event and data
        return await handler(event, data)
