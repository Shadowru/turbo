import json
import re


class LLMJsonParseError(ValueError):
    """Исключение, генерируемое при невозможности распарсить JSON из ответа LLM."""


CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def extract_json_from_response(raw: str) -> dict:
    """
    Извлекает JSON-объект из строки ответа LLM.

    Поддерживает форматы:
    - чистый JSON;
    - обёрнутый в ```json ... ```.

    Raises:
        LLMJsonParseError: если JSON не найден или невалиден.
    """
    if not raw or not raw.strip():
        raise LLMJsonParseError("LLM response is empty")

    stripped = raw.strip()

    # Удаляем Markdown-кодовые блоки
    stripped = CODE_FENCE_PATTERN.sub("", stripped).strip()

    # Пробуем прямой парсинг
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Пытаемся вытащить JSON через регулярку
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise LLMJsonParseError(f"Invalid JSON extracted: {exc}") from exc

    raise LLMJsonParseError("Unable to locate JSON object in LLM response")