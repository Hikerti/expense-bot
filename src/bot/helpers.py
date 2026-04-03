from src.core.schemas import ParsedExpense


def get_missing_fields(parsed: ParsedExpense) -> list[str]:
    """Возвращает список полей, которые нужно заполнить."""
    missing = []
    
    if parsed.category_code is None:
        missing.append("category")
    if parsed.account_code is None:
        missing.append("account")
    if parsed.tranche_code is None:
        missing.append("tranche")
    if parsed.is_recurring is None:
        missing.append("is_recurring")
    
    return missing


def update_parsed_from_callback(
    parsed: ParsedExpense,
    field_type: str,
    value: str
) -> ParsedExpense:
    """Обновляет parsed после выбора пользователем."""
    mapping = {
        "category": {"code_attr": "category_code", "prefix": "cat"},
        "account": {"code_attr": "account_code", "prefix": "acc"},
        "tranche": {"code_attr": "tranche_code", "prefix": "tr"},
        "recurring": {"code_attr": "is_recurring", "value_prefix": "rec"},
        "status": {"code_attr": "status", "prefix": "st"},
    }
    
    config = mapping.get(field_type)
    if not config:
        return parsed
    
    attr_name = config["code_attr"]
    
    # Обновляем нужное поле
    if attr_name in ("category_code", "account_code", "tranche_code"):
        # Для кодов — убираем префикс из value
        updated_value = value.replace(config["prefix"] + ":", "")
        setattr(parsed, attr_name, updated_value)
    elif attr_name == "is_recurring":
        # Для булевых значений
        setattr(parsed, attr_name, value == "true")
    elif attr_name == "status":
        # Для статуса
        from src.core.enums import TransactionStatus
        try:
            setattr(parsed, attr_name, TransactionStatus(value))
        except ValueError:
            pass
    
    return parsed