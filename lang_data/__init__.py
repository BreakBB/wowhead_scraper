from typing import List

from .en import FILTERS as EN_FILTERS
from .de import FILTERS as DE_FILTERS
from .fr import FILTERS as FR_FILTERS
from .es import FILTERS as ES_FILTERS
from .mx import FILTERS as MX_FILTERS
from .ru import FILTERS as RU_FILTERS
from .cn import FILTERS as CN_FILTERS
from .pt import FILTERS as PT_FILTERS
from .ko import FILTERS as KO_FILTERS


def get_filter_list_by_lang(lang: str) -> List[str]:
    if lang == "en":
        return EN_FILTERS
    elif lang == "de":
        return DE_FILTERS
    elif lang == "fr":
        return FR_FILTERS
    elif lang == "es":
        return ES_FILTERS
    elif lang == "mx":
        return MX_FILTERS
    elif lang == "ru":
        return RU_FILTERS
    elif lang == "cn":
        return CN_FILTERS
    elif lang == "pt":
        return PT_FILTERS
    elif lang == "ko":
        return KO_FILTERS
    else:
        raise ValueError("Language '{}' not supported".format(lang))
