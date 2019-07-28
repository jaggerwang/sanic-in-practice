import sqlalchemy as sa
import sqlalchemy.types as satypes

from ..utils import as_local

metadata = sa.MetaData()


class LocalDateTime(satypes.TypeDecorator):
    impl = satypes.DateTime

    def process_bind_param(self, value, dialect):
        return as_local(value)

    def process_result_value(self, value, dialect):
        return None if value is None else as_local(value)
