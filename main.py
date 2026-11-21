import shlex


# Mini Git에서 지원하는 명령어 목록
COMMANDS = {
    "INIT",
    "BRANCH",
    "SWITCH",
    "COMMIT",
    "LOG",
    "PATH",
    "ANCESTORS",
    "SEARCH"
}


def parse_command(user_input):
    # 사용자 입력을 명령어와 인자로 분리한다.

    try:
        parts = shlex.split(user_input)
    except ValueError:
        print("Invalid args")
        return None, None

    if not parts:
        return None, None

    command = parts[0].upper()
    args = parts[1:]

    return command, args


def execute_command(command, args):
    # 명령어 유효성을 검사하고 실행한다.
    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        return

    # 인자가 1개 필요한 명령어
    if command in { "INIT", "BRANCH", "SWITCH", "COMMIT", "ANCESTORS"}:
        if len(args) != 1:
            print("Invalid args")
            return

    # 인자가 2개 필요한 명령어
    elif command == "PATH":
        if len(args) != 2:
            print("Invalid args")
            return 

    # 옵션에 따라 인자 개수가 달라지는 명령어
    elif command in {"LOG", "SEARCH"}:
        if command == "LOG" and len(args) > 1:
            print("Invalid args")
            return

        if command == "SEARCH" and len(args) != 1:
            print("Invalid args")
            return

    print(f"Command recognized: {command}")
    print(f"Arguments: {args}")
    print("Function not implemented yet.")


def main():
    """Mini Git REPL을 실행한다."""
    print("Welcome to Mini Git!")
    print("Type exit or quit to close.")

    while True:
        try:
            user_input = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        # 종료 명령어
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # 입력 파싱
        command, args = parse_command(user_input)

        if command is None:
            continue

        # 명령어 실행
        execute_command(command, args)


if __name__ == "__main__":
    main()
