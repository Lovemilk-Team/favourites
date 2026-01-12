from datetime import datetime, UTC
import sqlalchemy.types as types

"""
由于一些原因, 使用 SQLModel/SQLAlchemy,
在 SQLite 数据库下存储的 python datetime.datetime 类型的字段在从数据库拿出数据时的 tzinfo 是 `None`,
导致 datetime 认为这是本地的时间, 会在非 UTC 时区的设备上出现时差.

同时, 部分库 (包括但不限于 fastapi.Response.set_cookie 的 `expires` 参数) 需要有 tzinfo 的 UTC 时间,
从而出现问题.

一个可能的解决方法是自己实现一个可用于 编码/解码 数据库内容的 UTCDatetime 类型, 使得 SQLAlchemy 在 ORM 时自动转换.

使用方法:
```
Field(..., sa_type=UTCDatetime)
```
"""


class UTCDatetime(types.TypeDecorator):
    impl = types.BIGINT

    cache_ok = True

    _ts_rate = 1000_000

    def process_bind_param(self, value: datetime | None, _dialect) -> int | None:
        if value is None:
            return None

        if value.tzinfo is None:
            value = value.astimezone(UTC)

        return round(value.timestamp() * type(self)._ts_rate)

    def process_result_value(self, value: int | None, _dialect) -> datetime | None:
        if value is None:
            return None

        datetime_obj = datetime.fromtimestamp(value / type(self)._ts_rate, tz=UTC)
        return datetime_obj
