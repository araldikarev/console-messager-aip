from client.framework import Context


class BaseController:
    """Класс-провайдер контекста."""

    def __init__(self, ctx: Context):
        """
        Инициализирует базовый контроллер.
        
        :param self: self
        :param ctx: Контекст.
        :type ctx: Context
        """
        self.ctx = ctx
