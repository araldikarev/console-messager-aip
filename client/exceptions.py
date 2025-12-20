class CommandException(Exception):
    """
    Базовое исключение для команд.
    """

    pass


class UnknownCommandException(CommandException):
    """
    Исключение о неизвестной команде.
    """

    pass


class ArgumentMismatchCommandException(CommandException):
    """
    Исключение о несоответствии аргументов команды.
    """

    pass


class ValueErrorCommandException(CommandException):
    """
    Исключение об ошибке приложенных значений команды.
    """

    pass
