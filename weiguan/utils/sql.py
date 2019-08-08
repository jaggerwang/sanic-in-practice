import sqlalchemy as sa
import sqlalchemy.types as satypes

from .datetime import as_local


class LocalDateTime(satypes.TypeDecorator):
    """本地化的SQLAlchemy时间类型
    """
    impl = satypes.DateTime

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return as_local(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        return as_local(value)
