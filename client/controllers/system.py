import inspect

from client.controllers.base import BaseController
from client.framework import command, CommandNode
from client.logger import log_info, log_ok


class SystemController(BaseController):

    @command("help")
    async def help_command(self):
        """
        Выводит список всех доступных команд.
        /help
        """
        if not self.ctx.router:
            log_info("Роутер команд недоступен.")
            return

        log_ok("\nСПИСОК КОМАНД:")

        self._print_node_help(self.ctx.router.root, prefix="")

        log_ok("---------------------\n")

    def _print_node_help(self, node: CommandNode, prefix: str):
        """
        Рекурсивно обходит ноды и печатает help.

        :param self: self
        :param node: Текущая нода.
        :type node: CommandNode
        :param prefix: Собранный префикс.
        :type prefix: str
        """
        command_names = sorted(node.children.keys())

        for name in command_names:
            child_node = node.children[name]
            full_name = prefix + name

            if child_node.is_group:
                self._print_node_help(child_node, full_name + " ")
                continue

            handler = child_node.handler

            doc_text = inspect.getdoc(handler)

            usage = "/" + full_name
            description = "Нет описания"

            if doc_text:
                lines = doc_text.split("\n")

                if len(lines) > 0:
                    first_line = lines[0].strip()
                    if first_line:
                        description = first_line

                for line in lines:
                    line = line.strip()
                    if line.startswith("/"):
                        usage = line
                        break

            log_info(f"{usage:<45} - {description}")
