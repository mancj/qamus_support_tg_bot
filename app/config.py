from dataclasses import dataclass

from environs import Env


@dataclass
class BotConfig:
    """
    Data class representing the configuration for the bot.

    Attributes:
    - TOKEN (str): The bot token.
    - DEV_ID (int): The developer's user ID.
    - GROUP_ID (int): The group chat ID.
    - BOT_EMOJI_ID (str): The custom emoji ID for the group's topic.
    """
    TOKEN: str
    DEV_ID: int
    GROUP_ID: int
    BOT_EMOJI_ID: str


@dataclass
class RedisConfig:
    """
    Data class representing the configuration for Redis.

    Attributes:
    - HOST (str): The Redis host.
    - PORT (int): The Redis port.
    - DB (int): The Redis database number.
    """
    HOST: str
    PORT: int
    DB: int

    def dsn(self) -> str:
        """
        Generates a Redis connection DSN (Data Source Name) using the provided host, port, and database.

        :return: The generated DSN.
        """
        return f"redis://{self.HOST}:{self.PORT}/{self.DB}"


@dataclass
class OpenAIConfig:
    """
    Data class representing the configuration for OpenAI.

    Attributes:
    - API_KEY (str): The OpenAI API key.
    - MODEL (str): The OpenAI model to use (e.g., gpt-4o-mini, gpt-4o).
    - KNOWLEDGE_BASE_PATH (str): Path to the knowledge base JSON file.
    """
    API_KEY: str
    MODEL: str
    KNOWLEDGE_BASE_PATH: str


@dataclass
class Config:
    """
    Data class representing the overall configuration for the application.

    Attributes:
    - bot (BotConfig): The bot configuration.
    - redis (RedisConfig): The Redis configuration.
    - openai (OpenAIConfig): The OpenAI configuration.
    """
    bot: BotConfig
    redis: RedisConfig
    openai: OpenAIConfig


def load_config() -> Config:
    """
    Load the configuration from environment variables and return a Config object.

    :return: The Config object with loaded configuration.
    """
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            TOKEN=env.str("BOT_TOKEN"),
            DEV_ID=env.int("BOT_DEV_ID"),
            GROUP_ID=env.int("BOT_GROUP_ID"),
            BOT_EMOJI_ID=env.str("BOT_EMOJI_ID"),
        ),
        redis=RedisConfig(
            HOST=env.str("REDIS_HOST"),
            PORT=env.int("REDIS_PORT"),
            DB=env.int("REDIS_DB"),
        ),
        openai=OpenAIConfig(
            API_KEY=env.str("OPENAI_API_KEY"),
            MODEL=env.str("OPENAI_MODEL", "gpt-4o-mini"),
            KNOWLEDGE_BASE_PATH=env.str("OPENAI_KNOWLEDGE_BASE_PATH", "knowledge_base.json"),
        ),
    )
