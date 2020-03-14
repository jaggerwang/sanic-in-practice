from datetime import datetime, timedelta, timezone

local_tz = timezone(timedelta(hours=8))


def local_now():
    return datetime.now().replace(tzinfo=local_tz)


def as_local(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=local_tz)
    else:
        return dt.astimezone(local_tz)
