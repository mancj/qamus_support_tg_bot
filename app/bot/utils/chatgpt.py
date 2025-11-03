from typing import Optional, List, Dict
import logging
import json
from pathlib import Path

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.config import OpenAIConfig


logger = logging.getLogger(__name__)


def load_knowledge_base(file_path: str) -> List[Dict[str, str]]:
    """
    Load knowledge base from JSON file.

    :param file_path: Path to the JSON file with QA pairs.
    :return: List of QA pairs.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Knowledge base file not found: {file_path}")
            return []

        with open(path, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)

        logger.info(f"Loaded {len(knowledge_base)} entries from knowledge base")
        return knowledge_base

    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        return []


class ChatGPTService:
    """
    Service for interacting with OpenAI ChatGPT API.

    Attributes:
    - client (AsyncOpenAI): The async OpenAI client.
    - model (str): The model to use for completions.
    - knowledge_base (List[Dict[str, str]]): QA knowledge base.
    """

    def __init__(self, config: OpenAIConfig):
        """
        Initialize the ChatGPT service.

        :param config: OpenAI configuration.
        """
        self.client = AsyncOpenAI(api_key=config.API_KEY)
        self.model = config.MODEL
        self.knowledge_base: List[Dict[str, str]] = []
        logger.info(f"ChatGPT service initialized with model: {self.model}")

    def set_knowledge_base(self, knowledge_base: List[Dict[str, str]]) -> None:
        """
        Set the knowledge base for the ChatGPT service.

        :param knowledge_base: List of QA pairs in format [{"question": "Q", "answer": "A"}, ...]
        """
        self.knowledge_base = knowledge_base
        logger.info(f"Knowledge base updated with {len(knowledge_base)} entries")

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt with knowledge base.

        :return: System prompt string.
        """
        base_prompt = (
            "Ты - дружелюбный ассистент службы поддержки. "
            "Твоя задача - помогать пользователям, отвечая на их вопросы естественно и по-человечески.\n\n"
            "У тебя есть база знаний - используй её как СПРАВОЧНИК для ответов. "
            "адаптируй под конкретный вопрос пользователя, добавь эмпатии и дружелюбия.\n\n"
            "ВАЖНЫЕ ПРАВИЛА:\n"
            "1. Если вопрос связан с информацией из базы знаний - дай естественный ответ\n"
            "2. Если ВОПРОСА НЕТ в базе знаний - ответь ТОЛЬКО словом: NO_ANSWER\n"
            "3. НЕ придумывай информацию, которой нет в базе знаний\n"
            "4. Будь кратким, но информативным (2-4 предложения)\n"
        )

        if self.knowledge_base:
            kb_text = "\n\n📚 БАЗА ЗНАНИЙ (справочная информация):\n"
            for i, qa in enumerate(self.knowledge_base, 1):
                kb_text += f"\n{i}. Тема: {qa['question']}\n   Информация: {qa['answer']}\n"
            base_prompt += kb_text

        return base_prompt

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatCompletionMessageParam]] = None,
    ) -> str:
        """
        Generate a response to user message using ChatGPT.

        :param user_message: The user's message.
        :param conversation_history: Optional conversation history.
        :return: Generated response.
        """
        try:
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": self._build_system_prompt()}
            ]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            logger.info(f"Generating response for message: {user_message[:50]}...")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.9,
                max_tokens=500,
            )

            generated_text = response.choices[0].message.content or ""
            logger.info(f"Response generated: {generated_text[:50]}...")

            return generated_text

        except Exception as e:
            logger.error(f"Error generating ChatGPT response: {e}")
            raise

    async def generate_response_with_context(
        self,
        user_message: str,
        previous_messages: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate a response with simplified conversation context.

        :param user_message: The user's message.
        :param previous_messages: List of previous messages in format [{"role": "user/assistant", "content": "..."}, ...]
        :return: Generated response.
        """
        conversation_history: List[ChatCompletionMessageParam] = []

        if previous_messages:
            for msg in previous_messages:
                if msg["role"] == "user":
                    conversation_history.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    conversation_history.append({"role": "assistant", "content": msg["content"]})

        return await self.generate_response(user_message, conversation_history)

    def has_valid_answer(self, response: str) -> bool:
        """
        Check if ChatGPT provided a valid answer (not NO_ANSWER).

        :param response: The response from ChatGPT.
        :return: True if valid answer, False otherwise.
        """
        return response.strip() != "NO_ANSWER" and len(response.strip()) > 0
