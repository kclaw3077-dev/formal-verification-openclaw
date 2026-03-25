from locales import en as _en, zh as _zh

_LOCALES = {"en": _en.SCENARIOS, "zh": _zh.SCENARIOS}


def get_locale(lang: str) -> dict:
    return _LOCALES.get(lang, _en.SCENARIOS)
