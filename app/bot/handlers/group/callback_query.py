from aiogram import Router, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import MagicData
from aiogram.types import CallbackQuery

from app.bot.manager import Manager
from app.bot.types.callback_data import ChatGPTResponseCallback

router = Router()
router.callback_query.filter(
    MagicData(F.event_chat.id == F.config.bot.GROUP_ID),  # type: ignore
    F.message.chat.type.in_(["group", "supergroup"]),
)


@router.callback_query(ChatGPTResponseCallback.filter())
async def handle_chatgpt_response(
    call: CallbackQuery,
    callback_data: ChatGPTResponseCallback,
    manager: Manager,
) -> None:
    """
    Handle ChatGPT response approval/rejection.

    :param call: CallbackQuery object.
    :param callback_data: ChatGPTResponseCallback data.
    :param manager: Manager object.
    :return: None
    """
    if callback_data.action == "approve":
        # Send ChatGPT response to user
        try:
            # Get the message text (ChatGPT response)
            chatgpt_response = call.message.text.split("\n\n", 1)[1] if "\n\n" in call.message.text else call.message.text

            await call.bot.send_message(
                chat_id=callback_data.user_id,
                text=chatgpt_response,
            )

            # Edit message to show it was sent
            await call.message.edit_text(
                text=f"✅ Ответ отправлен пользователю\n\n{chatgpt_response}",
                reply_markup=None,
            )

            await call.answer("Ответ отправлен пользователю")

        except TelegramAPIError as ex:
            if "blocked" in ex.message:
                await call.answer("Пользователь заблокировал бота", show_alert=True)
                await call.message.edit_text(
                    text=f"❌ Пользователь заблокировал бота\n\n{chatgpt_response}",
                    reply_markup=None,
                )
            else:
                await call.answer(f"Ошибка: {ex.message}", show_alert=True)

    elif callback_data.action == "reject":
        # Delete ChatGPT suggestion
        await call.message.delete()
        await call.answer("Предложенный ответ отклонен. Напишите свой ответ.")
