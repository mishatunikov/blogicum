from typing import Union


def get_short_text(text: str, max_worlds: int = 10,
                   max_symbols: Union[int, None] = None):
    """
    Сокращает строку до указанного количества символов | строк.
    Если задан параметр max_symbols, то сокращение будет по символам,
    если не задан, то по количеству слов.
    """
    if max_symbols:
        return (text if len(text) < max_symbols
                else text[:max_symbols] + '...')
    else:
        text_split = text.split()
        return (text if len(text_split) > max_worlds
                else ' '.join(text_split[:max_worlds]) + '...')
