import os

import redis


def get_redis_client() -> redis.Redis:
    """
    Создаёт клиента Redis, настроенного для работы внутри Docker-сети.

    Хост берётся из переменной окружения REDIS_HOST (по умолчанию 'redis' —
    так называется сервис в docker-compose.yml), порт — из REDIS_PORT (по
    умолчанию 6379). decode_responses=True, чтобы получать строки, а не bytes.
    """
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", "6379"))

    return redis.Redis(
        host=host,
        port=port,
        db=0,
        decode_responses=True,
    )


def main() -> None:
    client = get_redis_client()
    try:
        response = client.ping()
        print(f"PING response from Redis: {response}")
    except Exception as exc:  # простая проверка, без излишней обработки
        print(f"Failed to connect to Redis: {exc}")


if __name__ == "__main__":
    main()


