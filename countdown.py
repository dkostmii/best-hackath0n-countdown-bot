from typing import cast
from datetime import datetime, timedelta
from pluralize import pluralize_multiple


class CountdownData:
    countdown_dt: datetime
    end_dt: datetime
    now_dt: datetime
    _weekday_captions: list[str]

    def __init__(self, weekday_captions: list[str], data: dict[str, dict[str, str]]):
        self._weekday_captions = weekday_captions

        countdown_dt_iso = data["dts"]["countdown_dt_iso"]
        end_dt_iso = data["dts"]["end_dt_iso"]
        self.countdown_dt = datetime.fromisoformat(countdown_dt_iso)
        self.end_dt = datetime.fromisoformat(end_dt_iso)
        tz = self.countdown_dt.tzinfo
        self.now_dt = datetime.now(tz=tz)

        self.countdown_dt = self.countdown_dt.replace(second=0, microsecond=0)
        self.end_dt = self.end_dt.replace(second=0, microsecond=0)
        self.now_dt = self.now_dt.replace(second=0, microsecond=0)

    @property
    def now_weekday(self):
        return self._weekday_captions[self.now_dt.weekday()]
    
    @property
    def now_time_hh_mm(self):
        return self.now_dt.strftime("%H:%M")


def get_pluralizations_dicts_multiple(format: str, units: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    result = units

    if format == 'hours':
        result = {
            'hours': result["hours"],
            'minutes': result["minutes"]
        }
    elif format == 'minutes':
        result = {
            'minutes': result["minutes"]
        }

    return result


def get_pluralizations_values(format: str, delta: timedelta) -> dict[str, int]:
    min = int(delta.total_seconds() / 60)

    result = {
        'minutes': min
    }

    if format == 'hours':
        hours = min // 60
        min = min - hours * 60

        if hours != 0:
            result.update({'hours': hours, 'minutes': min})

        if min == 0:
            del result["minutes"]

    elif format == 'days':
        hours = min // 60
        min = min - hours * 60

        days = hours // 24
        hours = hours - days * 24

        if days != 0:
            result.update({'days': days, 'minutes': min})

        if hours != 0:
            result.update({'hours': hours, 'minutes': min})

        if min == 0:
            del result["minutes"]

    return result


def prepare_template_for_format(values: dict[str, int], template: str, format: str) -> str:
    result = template
    if format == "hours":
        result = result.replace("{days} ", "")
    elif format == "minutes":
        result = result.replace("{days} ", "").replace("{hours} ", "")

    if not "days" in values:
        result = result.replace("{days} ", "")

    if not "hours" in values:
        result = result.replace("{hours} ", "")

    if not "minutes" in values:
        result = result.replace(" {minutes}", "").replace("{minutes}", "")

    return result


def get_countdown_past_message(diff: timedelta, progress_timeout: timedelta, format: str, pluralizations_dicts_multiple: dict[str, dict[str, str]], templates: dict[str, str]) -> str:
    if diff < progress_timeout:
        remaining = progress_timeout - diff
        values = get_pluralizations_values(format, remaining)
        template = prepare_template_for_format(values=values, template=templates["past_progress"], format=format)
        message = pluralize_multiple(template, values, pluralizations_dicts_multiple)
    elif diff > progress_timeout:
        past = diff - progress_timeout
        values = get_pluralizations_values(format, past)
        template = prepare_template_for_format(values=values, template=templates["past"], format=format)
        message = pluralize_multiple(template, values, pluralizations_dicts_multiple)
    else:
        template = templates["past_now"]
        message = template

    return message


def get_countdown_message(cd: CountdownData, format: str, countdown_captions: dict[str, dict[str, dict[str, str] | str]]) -> str:
    templates = cast(dict[str, str], countdown_captions["templates"])
    units = cast(dict[str, dict[str, str]], countdown_captions["units"])

    pluralizations_dicts_multiple = get_pluralizations_dicts_multiple(format, units=units)

    if cd.countdown_dt < cd.now_dt:
        progress_timeout = cd.end_dt - cd.countdown_dt
        diff = cd.now_dt - cd.countdown_dt
        return get_countdown_past_message(diff, progress_timeout, format, pluralizations_dicts_multiple, templates)
    elif cd.countdown_dt > cd.now_dt:
        diff = cd.countdown_dt - cd.now_dt
        values = get_pluralizations_values(format, diff)
        template = prepare_template_for_format(values=values, template=templates["default"], format=format)
        message = pluralize_multiple(template, values, pluralizations_dicts_multiple, weekday=cd.now_weekday, time_hh_mm=cd.now_time_hh_mm)
        return message

    message = templates["now"]
    message = message.format(weekday=cd.now_weekday, time_hh_mm=cd.now_time_hh_mm)
    return message
