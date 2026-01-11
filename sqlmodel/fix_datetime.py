from datetime import UTC, datetime as original_datetime

"""
由于一些原因, 使用 SQLModel/SQLAlchemy,
在 SQLite 数据库下存储的 python datetime.datetime 类型的字段在从数据库拿出数据时的 tzinfo 是 `None`,
导致 datetime 认为这是本地的时间, 会在非 UTC 时区的设备上出现时差.

同时, 部分库 (包括但不限于 fastapi.Response.set_cookie 的 `expires` 参数) 需要有 tzinfo 的 UTC 时间,
从而出现问题

一个可能的解决方法是将 datetime.datetime class 替换, 并在 `__new__` 时将 tzinfo 为 `None` 的时间全部视为 UTC.
"""


def init_datetime():
    original_new = original_datetime.__new__
    original_now = original_datetime.now

    class UTCDatetime(original_datetime):
        max = original_datetime.max.replace(tzinfo=UTC)
        min = original_datetime.min.replace(tzinfo=UTC)

        def __new__(cls, *args, **kwargs):
            if len(args) >= 8:
                tzinfo = args[7]
                if tzinfo is None:
                    args = (*args[:7], UTC, *args[8:])
            else:
                tzinfo = kwargs.get("tzinfo", None)
                if tzinfo is None:
                    kwargs["tzinfo"] = UTC

            return original_new(cls, *args, **kwargs)  # type: ignore

        @classmethod
        def now(cls, tz=UTC):
            return original_now(tz)

    import datetime

    datetime.datetime = UTCDatetime
