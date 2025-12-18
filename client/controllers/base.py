from client.framework import Context


class BaseController:
    """Класс-провайдер контекста."""

    def __init__(self, ctx: Context):
        self.ctx = ctx
