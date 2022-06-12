import re
from datetime import timedelta
from itertools import cycle
from typing import Any, Callable, Iterable, Mapping, Tuple

BOOL_TRUE = {"y", "yes", "t", "true", "on", "1"}
BOOL_FALSE = {"n", "no", "f", "false", "off", "0"}
DURATIONS = m = {
    "d": "days",
    "h": "hours",
    "m": "minutes",
    "s": "seconds",
    "ms": "milliseconds",
    "µs": "microseconds",
}


find_durations = re.compile(r"([0-9]+)([µsmhd]+)").findall


def duration(src: str) -> timedelta:
    """
    duration("2m30s") == timedelta(minutes=2, seconds=30)
    """
    return timedelta(**{DURATIONS[k]: int(v) for v, k in find_durations(src)})


def boolean(src: str) -> bool:
    """
    Copied from
    https://github.com/python/cpython/blob/main/Lib/distutils/util.py#L308
    Is not part of 3.12 https://peps.python.org/pep-0632/
    :param src:
    :return:
    """

    s = src.lower()
    if s in BOOL_TRUE:
        return True

    if s in BOOL_FALSE:
        return False

    raise ValueError(f"invalid bool value {src!r}")


def parse_dict(
    cls: type, key: type, value: type, sep: Tuple[str, str] = (":", ",")
) -> Callable[[str], Mapping]:
    s1, s2 = sep

    def cast(s: str) -> Tuple[Any, Any]:
        k, v = s.split(s1)
        return key(k), value(v)

    return lambda s: cls(map(cast, s.split(s2)))


def parse_iter(
    cls: type, *types: type, sep: str = ","
) -> Callable[[str], Iterable]:
    fixed_tuple = issubclass(cls, tuple) and types[-1] is not ...
    if not fixed_tuple:
        # Tuple[foo, ...] - all items of the same type
        types = types[:1]

    def inner(s: str):
        items = s.split(sep)
        if fixed_tuple and len(types) != len(items):
            raise ValueError(
                "Invalid length for fixed tuple: expected %d, got %d"
                % (len(types), len(items)),
            )
        c = cycle(types)
        return cls(next(c)(v) for v in items)

    return inner
