import dataclasses
import datetime as dt
from typing import List
from typing import Optional


@dataclasses.dataclass
class ScheduledReset:
    park_id: str
    driver_id: str
    reason: str
    scheduled_at: dt.datetime
    source: Optional[str] = None


def insert_scheduled_resets(items: List[ScheduledReset]):
    source_to_sql_str = (
        lambda source: '\'' + source + '\'' if source else 'NULL'
    )
    return (
        """INSERT INTO state.scheduled_resets
        (park_id, driver_id, scheduled_at, reason, source) VALUES"""
        + ', '.join(
            f"""('{item.park_id}','{item.driver_id}',
            '{item.scheduled_at.isoformat()}',
            '{item.reason}',
             {source_to_sql_str(item.source)}
            )"""
            for item in items
        )
    )


def get_scheduled_mode_resets(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT
        park_id,
        driver_id,
        reason,
        scheduled_at,
        source
        FROM state.scheduled_resets
        ORDER BY park_id, driver_id
        """,
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(ScheduledReset(*row))
    return result
