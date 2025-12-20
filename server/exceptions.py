class ServerException(Exception):
    """
    Базовое исключение сервера.
    """

    pass


class ProtocolError(ServerException):
    """
    Исключение об ошибке протокола/формата пакета.
    """

    pass


class MissingActionError(ProtocolError):
    """
    Исключение о том, что в пакете отсутствует поле action.
    """

    pass


class UnknownActionError(ProtocolError):
    """
    Исключение о том, что action не зарегистрирован в роутере.
    """

    pass


class PacketValidationError(ProtocolError):
    """
    Исключение об ошибке валидации пакета.
    """

    pass


class UnauthorizedError(ServerException):
    """
    Исключение об ошибке авторизации.
    """

    pass


class DatabaseError(ServerException):
    """
    Исключение об ошибке работы с базой данных
    """

    pass


class InternalServerError(ServerException):
    """
    Исключение неожиданной ошибки сервера.
    """

    pass


class ExpiredSignatureServerError(UnauthorizedError):
    """
    Исключение о просроченном JWT токене.
    """

    pass


class InvalidTokenServerError(UnauthorizedError):
    """
    Исключение о невалидной JWT токене.
    """

    pass
