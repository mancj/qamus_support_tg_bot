from aiogram.filters.callback_data import CallbackData


class ChatGPTResponseCallback(CallbackData, prefix="chatgpt"):
    """
    Callback data for ChatGPT response approval/rejection.

    Attributes:
    - action: Action to perform ('approve' or 'reject')
    - user_id: ID of the user to send the response to
    - message_id: ID of the message with ChatGPT suggestion
    """
    action: str
    user_id: int
    message_id: int
