"""
Пример использования ChatGPT сервиса с базой знаний.

Этот пример демонстрирует:
1. Загрузку конфигурации
2. Инициализацию ChatGPT сервиса
3. Загрузку базы знаний
4. Генерацию ответов на вопросы пользователей
"""

import asyncio
from app.config import load_config
from app.bot.utils import ChatGPTService, load_knowledge_base


async def main():
    # Загрузка конфигурации
    config = load_config()

    # Инициализация ChatGPT сервиса
    chatgpt_service = ChatGPTService(config.openai)

    # Загрузка базы знаний
    knowledge_base = load_knowledge_base(config.openai.KNOWLEDGE_BASE_PATH)
    chatgpt_service.set_knowledge_base(knowledge_base)

    # Пример 1: Простой вопрос
    print("=" * 50)
    print("Пример 1: Простой вопрос")
    print("=" * 50)
    user_message = "Как связаться с поддержкой?"
    response = await chatgpt_service.generate_response(user_message)
    print(f"Пользователь: {user_message}")
    print(f"ChatGPT: {response}")

    # Пример 2: Вопрос с контекстом
    print("\n" + "=" * 50)
    print("Пример 2: Вопрос с контекстом")
    print("=" * 50)

    conversation_history = [
        {"role": "user", "content": "Я хочу вернуть товар"},
        {"role": "assistant", "content": "Конечно! Вы можете вернуть товар в течение 14 дней."},
    ]

    user_message = "А как это сделать?"
    response = await chatgpt_service.generate_response_with_context(
        user_message,
        conversation_history
    )
    print(f"Контекст: Пользователь уже спросил про возврат товара")
    print(f"Пользователь: {user_message}")
    print(f"ChatGPT: {response}")

    # Пример 3: Вопрос вне базы знаний
    print("\n" + "=" * 50)
    print("Пример 3: Вопрос вне базы знаний")
    print("=" * 50)
    user_message = "Какая погода сегодня?"
    response = await chatgpt_service.generate_response(user_message)
    print(f"Пользователь: {user_message}")
    print(f"ChatGPT: {response}")


if __name__ == "__main__":
    asyncio.run(main())
