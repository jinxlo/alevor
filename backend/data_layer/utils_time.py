"""Time utilities for data alignment and timestamp conversions."""

import time
from datetime import datetime, timedelta
from typing import Optional


def timestamp_to_datetime(ts: int) -> datetime:
    """Convert Unix timestamp to datetime."""
    return datetime.fromtimestamp(ts)


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp."""
    return int(dt.timestamp())


def align_to_candle_time(timestamp: int, interval_seconds: int) -> int:
    """Align timestamp to candle boundary.
    
    Args:
        timestamp: Unix timestamp
        interval_seconds: Candle interval in seconds (e.g., 300 for 5min)
    
    Returns:
        Aligned timestamp
    """
    return (timestamp // interval_seconds) * interval_seconds


def get_day_start(timestamp: int) -> int:
    """Get start of day (00:00:00 UTC) for given timestamp."""
    dt = timestamp_to_datetime(timestamp)
    day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime_to_timestamp(day_start)


def get_week_start(timestamp: int) -> int:
    """Get start of week (Monday 00:00:00 UTC) for given timestamp."""
    dt = timestamp_to_datetime(timestamp)
    days_since_monday = dt.weekday()
    week_start = dt - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime_to_timestamp(week_start)


def get_time_window(start_ts: int, end_ts: int, interval_seconds: int) -> list[int]:
    """Generate list of aligned timestamps in a time window.
    
    Args:
        start_ts: Start timestamp
        end_ts: End timestamp
        interval_seconds: Interval between timestamps
    
    Returns:
        List of aligned timestamps
    """
    start_aligned = align_to_candle_time(start_ts, interval_seconds)
    timestamps = []
    current = start_aligned
    
    while current <= end_ts:
        timestamps.append(current)
        current += interval_seconds
    
    return timestamps
