import asyncio
import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.types import Message

from app.bot.keyboards import get_chatgpt_approval_keyboard
from app.bot.manager import Manager
from app.bot.types.album import Album
from app.bot.utils import ChatGPTService
from app.bot.utils.create_forum_topic import (
    create_forum_topic,
    get_or_create_forum_topic,
)
from app.bot.utils.redis import RedisStorage
from app.bot.utils.redis.models import UserData

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.type == "private", StateFilter(None))


@router.edited_message()
async def handle_edited_message(message: Message, manager: Manager) -> None:
    """
    Handle edited messages.

    :param message: The edited message.
    :param manager: Manager object.
    :return: None
    """
    # Get the text for the edited message
    text = manager.text_message.get("message_edited")
    # Reply to the edited message with the specified text
    msg = await message.reply(text)
    # Wait for 5 seconds before deleting the reply
    await asyncio.sleep(5)
    # Delete the reply to the edited message
    await msg.delete()


@router.message(F.media_group_id)
@router.message(F.media_group_id.is_(None))
async def handle_incoming_message(
        message: Message,
        manager: Manager,
        redis: RedisStorage,
        user_data: UserData,
        chatgpt_service: ChatGPTService,
        album: Album | None = None,
) -> None:
    """
    Handles incoming messages and copies them to the forum topic.
    If the user is banned, the messages are ignored.
    Generates ChatGPT response and sends it to admin for approval.

    :param message: The incoming message.
    :param manager: Manager object.
    :param redis: RedisStorage object.
    :param user_data: UserData object.
    :param chatgpt_service: ChatGPT service instance.
    :param album: Album object or None.
    :return: None
    """
    # Check if the user is banned
    if user_data.is_banned:
        return

    async def copy_message_to_topic():
        """
        Copies the message or album to the forum topic.
        If no album is provided, the message is copied. Otherwise, the album is copied.
        """
        message_thread_id = await get_or_create_forum_topic(
            message.bot,
            redis,
            manager.config,
            user_data,
        )

        if not album:
            await message.forward(
                chat_id=manager.config.bot.GROUP_ID,
                message_thread_id=message_thread_id,
            )
        else:
            await album.copy_to(
                chat_id=manager.config.bot.GROUP_ID,
                message_thread_id=message_thread_id,
            )

        return message_thread_id

    try:
        message_thread_id = await copy_message_to_topic()
    except TelegramBadRequest as ex:
        if "message thread not found" in ex.message:
            user_data.message_thread_id = await create_forum_topic(
                message.bot,
                manager.config,
                user_data.full_name,
            )
            await redis.update_user(user_data.id, user_data)
            message_thread_id = await copy_message_to_topic()
        else:
            raise

    # Generate ChatGPT response if message has text
    if message.text:
        # Send "thinking" indicator to admin
        thinking_message = await message.bot.send_message(
            chat_id=manager.config.bot.GROUP_ID,
            message_thread_id=message_thread_id,
            text="🤔 <i>ChatGPT генерирует ответ...</i>",
        )

        try:
            chatgpt_response = await chatgpt_service.generate_response(message.text)

            # Check if ChatGPT has a valid answer
            if chatgpt_service.has_valid_answer(chatgpt_response):
                # Update thinking message with ChatGPT suggestion and approval buttons
                await thinking_message.edit_text(
                    text=f"💡 <b>Предложенный ответ от ChatGPT:</b>\n\n{chatgpt_response}",
                    reply_markup=get_chatgpt_approval_keyboard(
                        user_id=user_data.id,
                        message_id=message.message_id,
                    ),
                )
                logger.info(f"ChatGPT response sent to admin for user {user_data.id}")
            else:
                # Delete thinking message if no valid answer
                await thinking_message.edit_text(
                    text="ℹ️ <i>ChatGPT не нашел ответ в базе знаний. Пожалуйста, ответьте самостоятельно.</i>",
                )
                # Auto-delete after 5 seconds
                await asyncio.sleep(5)
                await thinking_message.delete()
                logger.info(f"ChatGPT has no answer for user {user_data.id} message")

        except Exception as e:
            logger.error(f"Error generating ChatGPT response: {e}")
            # Delete thinking message on error
            await thinking_message.edit_text(
                text="❌ <i>Ошибка при генерации ответа ChatGPT. Пожалуйста, ответьте самостоятельно.</i>",
            )
            await asyncio.sleep(5)
            await thinking_message.delete()

    # Send a confirmation message to the user
    text = manager.text_message.get("message_sent")
    # Reply to the edited message with the specified text
    msg = await message.reply(text)
    # Wait for 5 seconds before deleting the reply
    await asyncio.sleep(5)
    # Delete the reply to the edited message
    await msg.delete()
