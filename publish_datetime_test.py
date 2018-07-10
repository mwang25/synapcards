import datetime
import pytz
import unittest

from publish_datetime import PublishDatetime
from publish_datetime import PublishDatetimeError


class TestPublishDatetime(unittest.TestCase):

    def test_supported_formats(self):
        self.assertEqual(
            set(PublishDatetime.SUPPORTED_FORMATS),
            set(['%Y', '%B %Y', '%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']))

    def test_year(self):
        dt = datetime.datetime(year=1999, month=1, day=1)
        pdt = PublishDatetime.parse_string('1999')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(pdt.output_format, '%Y')
        self.assertEqual(str(pdt), '1999')

    def test_month_year(self):
        dt = datetime.datetime(year=2000, month=7, day=1)
        pdt = PublishDatetime.parse_string('7/2000')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(pdt.output_format, '%B %Y')
        self.assertEqual(str(pdt), 'July 2000')

        # confirm leading 0 can be omitted
        pdt = PublishDatetime.parse_string('07/2000')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(pdt.output_format, '%B %Y')
        self.assertEqual(str(pdt), 'July 2000')

        pdt = PublishDatetime.parse_string('July 2000')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(pdt.output_format, '%B %Y')
        self.assertEqual(str(pdt), 'July 2000')

    def test_month_day_year(self):
        dt = datetime.datetime(year=2001, month=5, day=9)
        pdt = PublishDatetime.parse_string('05/09/2001')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(pdt.output_format, '%m/%d/%Y')
        self.assertEqual(str(pdt), '05/09/2001')

        # confirm leading 0 can be omitted
        pdt = PublishDatetime.parse_string('5/9/2001')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(pdt.output_format, '%m/%d/%Y')
        self.assertEqual(str(pdt), '05/09/2001')

    def test_timestamp(self):
        dt = datetime.datetime(
            year=2002, month=12, day=20, hour=1, minute=30, second=59)
        pdt = PublishDatetime.parse_string('2002-12-20 01:30:59')
        self.assertEqual(pdt.datetime, dt)
        self.assertEqual(
            pdt.output_format, PublishDatetime.CREATE_UPDATE_FORMAT)
        self.assertEqual(str(pdt), '2002-12-20 01:30:59')

        # Localize to US/Pacific timezone
        pdt.set_timezone('US/Pacific')
        utc_tzinfo = pytz.timezone('UTC')
        loc_tzinfo = pytz.timezone('US/Pacific')
        loc_dt = dt.replace(tzinfo=utc_tzinfo).astimezone(loc_tzinfo)
        self.assertEqual(pdt.datetime, loc_dt)
        self.assertEqual(
            pdt.output_format, PublishDatetime.CREATE_UPDATE_FORMAT)
        self.assertEqual(str(pdt), '2002-12-19 17:30:59')

        # Check daylight saving time in US/Pacific
        dt = datetime.datetime(
            year=2002, month=7, day=20, hour=1, minute=30, second=59)
        loc_dt = dt.replace(tzinfo=utc_tzinfo).astimezone(loc_tzinfo)
        pdt = PublishDatetime.parse_string('2002-07-20 01:30:59')
        pdt.set_timezone('US/Pacific')
        self.assertEqual(pdt.datetime, loc_dt)
        self.assertEqual(
            pdt.output_format, PublishDatetime.CREATE_UPDATE_FORMAT)
        self.assertEqual(str(pdt), '2002-07-19 18:30:59')

    def test_errors(self):
        # 2 digit year
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('99')
        self.assertEquals('Bad date format', cm.exception.message)

        # out of range month
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('13/1999')
        self.assertEquals('Bad date format', cm.exception.message)

        # out of range month
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('13/2/1999')
        self.assertEquals('Bad date format', cm.exception.message)

        # out of range date
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('12/32/1999')
        self.assertEquals('Bad date format', cm.exception.message)

        # too many digits
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('150/1999')
        self.assertEquals('Bad date format', cm.exception.message)

        # abbreviated month name
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('Jan 1999')
        self.assertEquals('Bad date format', cm.exception.message)

        # complete junk
        with self.assertRaises(PublishDatetimeError) as cm:
            PublishDatetime.parse_string('blah')
        self.assertEquals('Bad date format', cm.exception.message)


if __name__ == '__main__':
    unittest.main()
