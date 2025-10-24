from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.types.callback_data import ChatGPTResponseCallback


def get_chatgpt_approval_keyboard(user_id: int, message_id: int) -> InlineKeyboardMarkup:
    """
    Create inline keyboard for ChatGPT response approval/rejection.

    :param user_id: ID of the user to send the response to.
    :param message_id: ID of the message with ChatGPT suggestion.
    :return: InlineKeyboardMarkup with approval/rejection buttons.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Отправить",
                    callback_data=ChatGPTResponseCallback(
                        action="approve",
                        user_id=user_id,
                        message_id=message_id,
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=ChatGPTResponseCallback(
                        action="reject",
                        user_id=user_id,
                        message_id=message_id,
                    ).pack()
                ),
            ]
        ]
    )
