import datetime
from datetime import date, timedelta

from nose.tools import eq_

from services.time_ import get_datetime


def test_times():
    today = date.today()
    today = datetime.datetime(year=today.year, month=today.month, day=today.day)
    
    def test(query, then):
        eq_(get_datetime(query), then)

    yield test, "today", today
    yield test, "this morning", today + timedelta(hours=6)
    yield test, "this afternoon", today + timedelta(hours=12)
    yield test, "this evening", today + timedelta(hours=18)
    yield test, "this night", today + timedelta(hours=21)
    yield test, "tonight", today + timedelta(hours=21)
    yield test, "tomorrow", today + timedelta(days=1)
    yield test, "yesterday", today + timedelta(days=-1)
    yield test, "yesterday morning", today + timedelta(days=-1, hours=6)
    yield test, "yesterday afternoon", today + timedelta(days=-1, hours=12)
    yield test, "yesterday evening", today + timedelta(days=-1, hours=18)
    yield test, "yesterday night", today + timedelta(days=-1, hours=21)
    yield test, "last night", today + timedelta(days=-1, hours=21)
    yield test, "this week", today + timedelta(days=3)
    yield test, "this month", today + timedelta(days=14)
    yield test, "this year", today + timedelta(weeks=26)
    yield test, "next week", today + timedelta(days=7)
    yield test, "next month", today + timedelta(weeks=4)
    yield test, "next year", today + timedelta(weeks=52)
