from client.framework import Context

class BaseController:
    def __init__(self, ctx: Context):
        self.ctx = ctx

        