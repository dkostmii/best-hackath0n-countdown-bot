def pluralize(n: int = 1, pluralizations_dict: dict[str, str] = {}, **kwargs) -> str:
    if n == 0:
        if pluralizations_dict["zero"] is None:
            return pluralizations_dict["one"].format(n=1, **kwargs)

        return pluralizations_dict["zero"].format(n=n, **kwargs)

    last_digit = n % 10
    is_nteen = 10 <= n <= 19

    if last_digit == 1 and not is_nteen:
        return pluralizations_dict["one"].format(n=n, **kwargs)
    
    if 2 <= last_digit <= 4 and not is_nteen:
        if pluralizations_dict["few"] is None:
            return pluralizations_dict["one"].format(n=1, **kwargs)
        
        return pluralizations_dict["few"].format(n=n, **kwargs)

    if pluralizations_dict["many"] is None:
        return pluralizations_dict["one"].format(n=1, **kwargs)

    return pluralizations_dict["many"].format(n=n, **kwargs)


def pluralize_multiple(template: str, values: dict[str, int], pluralizations_dicts_multiple: dict[str, dict[str, str]], **kwargs) -> str:
    result = template

    for k, v in values.items():
        n = v
        pluralizations_dict = pluralizations_dicts_multiple[k]
        pluralization = pluralize(n, pluralizations_dict, **kwargs)
        result = result.replace("{" + k + "}", pluralization)

    result = result.format(**kwargs)

    return result
