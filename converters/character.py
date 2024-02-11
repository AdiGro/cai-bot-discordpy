from typing import List, Union
from discord.app_commands import Transformer
from discord.app_commands import Choice
from discord.interactions import Interaction
from models.characters import characters


import logging
import traceback as tb
import inspect
from functools import wraps

logger = logging.getLogger("autocompletes")


def try_except(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        except Exception as e:
            tb.print_exception(type(e), e, e.__traceback__)
            logger.error(f"Error in {func.__name__}: {e}")
            raise e

    return wrapper


class CharacterTransformer(Transformer):
    async def transform(self, interaction, option):
        return option

    async def autocomplete(
        self, interaction: Interaction, value: str
    ) -> List[Choice[str]]:
        return [Choice(name=char["name"], value=char["char_id"]) for char in characters]
