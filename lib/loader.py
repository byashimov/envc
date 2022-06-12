import inspect
import os
from datetime import timedelta
from typing import Any, Callable, Dict, Iterable, Mapping, Tuple, Type, TypeVar

from .classifiers import boolean, duration, parse_dict, parse_iter
from .compat import get_args, get_origin

ATTR = "__envc__"
T = TypeVar("T")
Class = Type[T]
Classifier = Callable[[type], Callable]
EMPTY = inspect._empty


class EnvconfigError(Exception):
    """
    Env config loader error
    """


def classifier_orig(cls: Class) -> Callable:
    """
    Returns casting callback for the given type.
    :raises TypeError: for unknown type
    :raises EnvconfigError: if cls is a postponed evaluation
    """

    # Unpacks generic classes
    origin: Class = get_origin(cls) or cls

    if isinstance(origin, str):
        raise EnvconfigError(
            f"Postponed evaluation of annotations is not supported: {cls}"
        )

    if issubclass(origin, bool):
        return boolean

    if issubclass(origin, (int, str)):
        return origin

    if issubclass(origin, float):
        return lambda s: float(s.replace(",", "."))

    if issubclass(origin, timedelta):
        return duration

    if issubclass(origin, Mapping):
        # Default type `str` for key and value
        return parse_dict(origin, *(get_args(cls) or (str, str)))

    if issubclass(origin, Iterable):
        # Default type `str` for all elements
        return parse_iter(origin, *(get_args(cls) or (str,)))

    raise TypeError(f"{cls!r} unknown type")


def load(
    cls: Class,
    *,
    prefix: str = "",
    classifier: Classifier = classifier_orig,
) -> T:
    """
    Loads cls values from environment variables
    :param cls: Config class
    :param prefix: Env var names prefix
    :param classifier: Value type determiner
    :return: Instance of given `cls`
    """

    return _load(cls, prefix, classifier, EMPTY)


def _load(cls: Class, prefix: str, classifier: Classifier, default: Any) -> T:
    init: Dict[str, Any] = {}
    keys: Dict[str, str] = getattr(cls, ATTR, {})
    for klass, name, value in signature(cls, default):
        if name in keys:
            key = keys[name]
        elif prefix:
            key = f"{prefix}_{name}".upper()
        else:
            key = name.upper()

        try:
            cast = classifier(klass)
        except TypeError:
            init[name] = _load(klass, key, classifier, value)
        else:
            var = os.getenv(key)
            if var is None:
                if value is not EMPTY:
                    init[name] = value
                    continue
                raise EnvconfigError(f"{key} is required")

            try:
                init[name] = cast(var)
            except ValueError as e:
                raise EnvconfigError(
                    f"Can't cast {key}={var} to {klass!r}: {e}"
                ) from e

    return cls(**init)


def signature(cls: Class, default=EMPTY) -> Iterable[Tuple[Class, str, Any]]:
    fields = inspect.signature(cls.__init__).parameters
    for name, field in fields.items():
        if field.annotation is EMPTY:
            # it is "self", skip it whatever it's named after
            continue

        # If there is a default value, it has same field
        # If it doesn't, then some magic is used there
        value = field.default
        if default is not EMPTY:
            value = getattr(default, name, value)

        yield field.annotation, name, value
