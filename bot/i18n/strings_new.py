DEFAULT_LOCALE = "vi"

from .string_ru import TRANSLATIONS as TRANSLATIONS_RU
from .string_en import TRANSLATIONS as TRANSLATIONS_EN
from .string_vi import TRANSLATIONS as TRANSLATIONS_VI

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": TRANSLATIONS_RU,
    "en": TRANSLATIONS_EN,
    "vi": TRANSLATIONS_VI,
}