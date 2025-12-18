import html
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style

style = Style.from_dict(
    {
        "prompt": "ansicyan bold",
        "server": "ansigreen",
        "error": "ansired",
        "info": "ansiyellow",
        "notify": "ansipurple bold",
    }
)


def log_ok(text: str) -> None:
    """
    Логирует текст с статусом OK (success)

    :param text: Текст.
    :type text: str
    """
    print_formatted_text(
        HTML(f"<server>{html.escape(str(text))}</server>"), style=style
    )


def log_error(text: str) -> None:
    """
    Логирует текст с статусом ERROR

    :param text: Текст.
    :type text: str
    """
    print_formatted_text(HTML(f"<error>{html.escape(str(text))}</error>"), style=style)


def log_info(text: str) -> None:
    """
    Логирует текст с статусом INFO

    :param text: Текст.
    :type text: str
    """
    print_formatted_text(HTML(f"<info>{html.escape(str(text))}</info>"), style=style)


def log_notify(text: str) -> None:
    """
    Логирует текст с статусом NOTIFY (уведомление)

    :param text: Текст.
    :type text: str
    """
    print_formatted_text(
        HTML(f"<notify>{html.escape(str(text))}</notify>"), style=style
    )
