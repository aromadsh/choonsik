import json
import shlex

from mini_redis import MiniRedis
from pubsub import PubSub

INTEGER_ERROR = (
    "(error) ERR value is not an integer or out of range"
)

# 0 이상의 정수 파싱
def parse_nonnegative_integer(value):
    try:
        number = int(value)

        if number < 0:
            raise ValueError

        return number

    except ValueError:
        return None

# 음수를 포함한 정수를 파싱
def parse_integer(value):
    try:
        return int(value)

    except ValueError:
        return None

# 사용자 명령어를 실행하고 레디스 스타일 결과를 반환
def execute(db, line, pubsub=None):
    try:
        args = shlex.split(line)

    except ValueError:
        return "(error) ERR invalid quoting"

    if not args:
        return ""

    cmd = args[0].upper()
    argc = len(args)

    commands = (
        "SET", "GET", "DEL", "EXISTS", "DBSIZE",
        "KEYS", "CONFIG", "INFO", "EXPIRE", "TTL",
        "SUBSCRIBE", "UNSUBSCRIBE", "PUBLISH", "RECEIVE"
    )

    if cmd not in commands:
        return f"(error) ERR unknown command '{args[0]}'"

    if cmd == "SET":
        if argc != 3:
            return (
                "(error) ERR wrong number of arguments "
                "for 'SET' command"
            )

        return db.set(args[1], args[2])

    if cmd in ("GET", "DEL", "EXISTS", "TTL"):
        if argc != 2:
            return (
                "(error) ERR wrong number of arguments "
                f"for '{cmd}' command"
            )

        if cmd == "GET":
            value = db.get(args[1])

            if value is None:
                return "(nil)"

            return json.dumps(value, ensure_ascii=False)

        if cmd == "DEL":
            return f"(integer) {db.delete(args[1])}"

        if cmd == "EXISTS":
            return f"(integer) {db.exists(args[1])}"

        return f"(integer) {db.ttl(args[1])}"

    if cmd in ("DBSIZE", "KEYS"):
        if argc != 1:
            return (
                "(error) ERR wrong number of arguments "
                f"for '{cmd}' command"
            )

        if cmd == "DBSIZE":
            return f"(integer) {db.dbsize()}"

        result = db.keys()

        if result.size() == 0:
            return "(empty array)"

        return "\n".join(
            f"{i + 1}. "
            f"{json.dumps(result.get(i), ensure_ascii=False)}"
            for i in range(result.size())
        )

    if cmd == "CONFIG":
        if argc != 4:
            return (
                "(error) ERR wrong number of arguments "
                "for 'CONFIG' command"
            )

        if (
            args[1].upper() != "SET"
            or args[2].lower() != "maxmemory"
        ):
            return "(error) ERR unsupported CONFIG option"

        number = parse_nonnegative_integer(args[3])

        if number is None:
            return INTEGER_ERROR

        return db.config_set_maxmemory(number)

    if cmd == "INFO":
        if argc != 2:
            return (
                "(error) ERR wrong number of arguments "
                "for 'INFO' command"
            )

        if args[1].lower() != "memory":
            return "(error) ERR unsupported INFO section"

        return db.info_memory()

    if cmd == "EXPIRE":
        if argc != 3:
            return (
                "(error) ERR wrong number of arguments "
                "for 'EXPIRE' command"
            )

        seconds = parse_integer(args[2])

        if seconds is None:
            return INTEGER_ERROR

        return f"(integer) {db.expire(args[1], seconds)}"

    if cmd == "RECEIVE":
        if argc != 2:
            return (
                "(error) ERR wrong number of arguments "
                "for 'RECEIVE' command"
            )

        messages = pubsub.receive(args[1])

        if messages.size() == 0:
            return "(empty array)"

        return "\n".join(
            f"{i + 1}. "
            f"{json.dumps(messages.get(i), ensure_ascii=False)}"
            for i in range(messages.size())
        )

    if cmd in ("SUBSCRIBE", "UNSUBSCRIBE", "PUBLISH"):
        if argc != 3:
            return (
                "(error) ERR wrong number of arguments "
                f"for '{cmd}' command"
            )

        if cmd == "SUBSCRIBE":
            return (
                f"(integer) "
                f"{pubsub.subscribe(args[1], args[2])}"
            )

        if cmd == "UNSUBSCRIBE":
            return (
                f"(integer) "
                f"{pubsub.unsubscribe(args[1], args[2])}"
            )

        return (
            f"(integer) "
            f"{pubsub.publish(args[1], args[2])}"
        )

# 미니 레디스 REPL 실행
def main():
    db = MiniRedis()
    pubsub = PubSub()

    while True:
        try:
            line = input("mini-redis> ")

        except (EOFError, KeyboardInterrupt):
            print()
            break

        if line.strip().lower() in ("exit", "quit"):
            break

        result = execute(db, line, pubsub)

        if result:
            print(result)


if __name__ == "__main__":
    main()