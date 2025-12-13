from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style

style = Style.from_dict({
    'prompt': 'ansicyan bold',
    'server': 'ansigreen',
    'error': 'ansired',
    'info': 'ansiyellow',
    'notify': 'ansipurple bold'
})

def log_ok(text: str) -> None:
    print_formatted_text(HTML(f"<server>{text}</server>"), style=style)

def log_error(text: str) -> None:
    print_formatted_text(HTML(f"<error>{text}</error>"), style=style)

def log_info(text: str) -> None:
    print_formatted_text(HTML(f"<info>{text}</info>"), style=style)

def log_notify(text: str) -> None:
    print_formatted_text(HTML(f"<notify>{text}</notify>"), style=style)