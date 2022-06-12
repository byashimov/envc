try:
    from typing import get_args, get_origin
except ImportError:  # pragma: py-gte-38
    # Those are for py <= 3.7

    def get_origin(cls):  # type: ignore
        origin = None
        while True:
            cls = getattr(cls, "__origin__", None)
            if cls is None:
                return origin
            origin = cls

    def get_args(cls):  # type: ignore
        if get_origin(cls) is not None and hasattr(cls, "__args__"):
            return cls.__args__
        return ()
