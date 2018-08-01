import datetime
import pytz


class PublishDatetimeError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class PublishDatetime:
    CREATE_UPDATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    MDY_FORMAT = '%m/%d/%Y'
    SUPPORTED_FORMATS = [
        '%Y',
        '%B %Y',
        '%m/%Y',
        MDY_FORMAT,
        CREATE_UPDATE_FORMAT]

    def __init__(self, dt=None, output_format=None):
        self.datetime = dt
        self.output_format = output_format

    @classmethod
    def parse_string(cls, s):
        # As special case, if s is blank, leave object uninitialized
        if not s or len(s) == 0:
            return cls()

        try:
            dt = datetime.datetime.strptime(s, cls.CREATE_UPDATE_FORMAT)
            return cls(dt, cls.CREATE_UPDATE_FORMAT)
        except:
            # fall through and try the other formats
            pass

        # YYYY
        try:
            dt = datetime.datetime.strptime(s, '%Y')
            return cls(dt, '%Y')
        except:
            pass

        # mm/YYYY
        try:
            dt = datetime.datetime.strptime(s, '%m/%Y')
            # Use the month name even when input is month number
            return cls(dt, '%B %Y')
        except:
            pass

        # Month YYYY
        try:
            dt = datetime.datetime.strptime(s, '%B %Y')
            return cls(dt, '%B %Y')
        except:
            pass

        # mm/dd/YYYY
        try:
            dt = datetime.datetime.strptime(s, '%m/%d/%Y')
            return cls(dt, cls.MDY_FORMAT)
        except:
            pass

        raise PublishDatetimeError('Bad date format')

    def __str__(self):
        if self.datetime and self.output_format:
            return self.datetime.strftime(self.output_format)
        else:
            return ''

    def set_timezone(self, tzname):
        # If datetime is naive, assume it is UTC
        if not self.datetime.tzname():
            self.datetime = self.datetime.replace(tzinfo=pytz.timezone('UTC'))
        # Adjust datetime to specified tzname
        loc_tzinfo = pytz.timezone(tzname)
        self.datetime = self.datetime.astimezone(loc_tzinfo)
