from typing import List

from test_redis import get_redis_client


def demo_strings() -> None:
    """
    Демонстрация работы со строками в Redis.

    - SET с TTL (EX)
    - GET значения
    - TTL оставшееся время жизни ключа
    """
    client = get_redis_client()
    key = "str:greeting"

    print("\n--- STRINGS ---")
    # Устанавливаем значение строки с временем жизни 60 секунд
    client.set(key, "Hello, Redis!", ex=60)
    value = client.get(key)
    ttl = client.ttl(key)

    print(f"SET {key} = 'Hello, Redis!' (ttl=60)")
    print(f"GET {key} -> {value}")
    print(f"TTL {key} -> {ttl} сек.")

    # Очистка
    client.delete(key)
    print(f"DEL {key}")


def demo_lists() -> None:
    """
    Демонстрация работы со списками в Redis.

    - LPUSH (добавление слева)
    - RPUSH (добавление справа)
    - LRANGE (чтение диапазона элементов)
    """
    client = get_redis_client()
    key = "list:numbers"

    print("\n--- LISTS ---")
    client.delete(key)  # на всякий случай очищаем перед демонстрацией

    # Добавляем элементы слева
    client.lpush(key, 3)
    client.lpush(key, 2)
    client.lpush(key, 1)
    print(f"LPUSH {key} 3, 2, 1")

    # Добавляем элементы справа
    client.rpush(key, 4, 5)
    print(f"RPUSH {key} 4, 5")

    # Получаем весь список
    items: List[str] = client.lrange(key, 0, -1)
    print(f"LRANGE {key} 0 -1 -> {items}")

    # Очистка
    client.delete(key)
    print(f"DEL {key}")


def demo_sets() -> None:
    """
    Демонстрация работы с множествами в Redis.

    - SADD (добавление элементов)
    - SMEMBERS (получение всех элементов)
    - SISMEMBER (проверка вхождения)
    """
    client = get_redis_client()
    key = "set:colors"

    print("\n--- SETS ---")
    client.delete(key)

    client.sadd(key, "red", "green", "blue", "red")
    print(f"SADD {key} 'red', 'green', 'blue', 'red'")

    members = client.smembers(key)
    print(f"SMEMBERS {key} -> {members}")

    is_member_red = client.sismember(key, "red")
    is_member_yellow = client.sismember(key, "yellow")
    print(f"SISMEMBER {key} 'red' -> {is_member_red}")
    print(f"SISMEMBER {key} 'yellow' -> {is_member_yellow}")

    client.delete(key)
    print(f"DEL {key}")


def demo_hashes() -> None:
    """
    Демонстрация работы с хэшами в Redis.

    - HSET (установка полей)
    - HGETALL (получение всех полей)
    - HGET (получение конкретного поля)
    """
    client = get_redis_client()
    key = "hash:user:1"

    print("\n--- HASHES ---")
    client.delete(key)

    client.hset(key, mapping={"name": "Alice", "age": "30", "email": "alice@example.com"})
    print(f"HSET {key} name='Alice', age='30', email='alice@example.com'")

    all_fields = client.hgetall(key)
    print(f"HGETALL {key} -> {all_fields}")

    name = client.hget(key, "name")
    age = client.hget(key, "age")
    print(f"HGET {key} 'name' -> {name}")
    print(f"HGET {key} 'age' -> {age}")

    client.delete(key)
    print(f"DEL {key}")


def demo_sorted_sets() -> None:
    """
    Демонстрация работы с упорядоченными множествами (sorted sets) в Redis.

    - ZADD (добавление элементов с "весами" / score)
    - ZRANGE (получение диапазона с учётом сортировки по score)
    """
    client = get_redis_client()
    key = "zset:scores"

    print("\n--- SORTED SETS ---")
    client.delete(key)

    # ZADD принимает пары score -> member
    client.zadd(key, {"Bob": 10, "Alice": 50, "Charlie": 30})
    print(f"ZADD {key} Bob=10, Alice=50, Charlie=30")

    # Получаем элементы по возрастанию score
    # withscores=True вернёт пары (member, score)
    items_with_scores = client.zrange(key, 0, -1, withscores=True)
    print(f"ZRANGE {key} 0 -1 WITHSCORES -> {items_with_scores}")

    client.delete(key)
    print(f"DEL {key}")


def main() -> None:
    """
    Запускает демонстрации всех основных структур данных Redis.

    Скрипт предполагается запускать внутри контейнера приложения:
    docker-compose exec app python redis_data_structures.py
    """
    demo_strings()
    demo_lists()
    demo_sets()
    demo_hashes()
    demo_sorted_sets()


if __name__ == "__main__":
    main()


