def pluralize(n: int = 1, pluralizations_dict: dict[str, str] = {}, **kwargs) -> str | None:
    if n == 0:
        return pluralizations_dict["zero"].format(n=n, **kwargs)

    last_digit = n % 10
    is_nteen = 10 <= n <= 19

    if last_digit == 1:
        return pluralizations_dict["one"].format(n=n, **kwargs)
    
    if 2 <= last_digit <= 4 and not is_nteen:
        if pluralizations_dict["few"] is None:
            return pluralizations_dict["one"].format(n=n, **kwargs)
        
        return pluralizations_dict["few"].format(n=n, **kwargs)

    return pluralizations_dict["many"].format(n=n, **kwargs)