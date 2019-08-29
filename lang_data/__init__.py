from typing import List

from .en import QUEST as EN_QUEST, FILTERS as EN_FILTERS, REGEX as EN_REGEX
from .de import QUEST as DE_QUEST, FILTERS as DE_FILTERS
from .fr import QUEST as FR_QUEST, FILTERS as FR_FILTERS
from .es import QUEST as ES_QUEST, FILTERS as ES_FILTERS
from .ru import QUEST as RU_QUEST, FILTERS as RU_FILTERS, REGEX as RU_REGEX


def get_quest_str_by_lang(lang: str) -> str:
    if lang == "en":
        return EN_QUEST
    elif lang == "de":
        return DE_QUEST
    elif lang == "fr":
        return FR_QUEST
    elif lang == "es":
        return ES_QUEST
    elif lang == "ru":
        return RU_QUEST
    else:
        raise ValueError("Language '{}' not supported".format(lang))


def get_filter_list_by_lang(lang: str) -> List[str]:
    if lang == "en":
        return EN_FILTERS
    elif lang == "de":
        return DE_FILTERS
    elif lang == "fr":
        return FR_FILTERS
    elif lang == "es":
        return ES_FILTERS
    elif lang == "ru":
        return RU_FILTERS
    else:
        raise ValueError("Language '{}' not supported".format(lang))


def get_regex_list_by_lang(lang: str) -> List[str]:
    if lang == "en":
        return EN_REGEX
    elif lang == "ru":
        return RU_REGEX
    elif lang == "de" or lang == "fr" or lang == "es":
        return []
    else:
        raise ValueError("Language '{}' not supported".format(lang))
