"""
Firebase configuration
"""
import os
from datetime import datetime, timedelta
import math

class BaseConfig:
    """Base class for configuration
    """

    def __init__(self, file, cfg_psr):
        self.file = file
        self.parser = cfg_psr

    def _check_file(self):
        if not os.path.exists(self.file):
            raise FileNotFoundError(f"Config file not found, file: {self.file}")

    def read(self):
        self._check_file()
        # read file
        self.parser.read(self.file)

        return self

    def value(self, section, option):
        # get a value for a specific section and option
        return self.parser.get(section, option)


class FirebaseConfig:
    """Config class for firebase
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.section = "firebase"

    @property
    def database_url(self):
        return self.cfg.value(self.section, "database_url")


class EntsoeConfig:
    """Config class for entsoe
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.section = "entsoe"

    @property
    def endpoint(self):
        return self.cfg.value(self.section, "endpoint")

    @property
    def resources(self):
        return [res.strip() for res in self.cfg.value(self.section, "resources").split(",")]

    @property
    def params(self):
        PeriodStart, PeriodEnd = self.getTime()
        print(PeriodStart, PeriodEnd    )
        return {
            "securityToken": self.cfg.value(self.section, "securityToken"),
            "documentType" : self.cfg.value(self.section, "documentType"),
            "processType"  : self.cfg.value(self.section, "processType"),
            "in_Domain"    : self.cfg.value(self.section, "in_Domain"),
            "psrType"      : self.cfg.value(self.section, "psrType"),
            "periodStart"  : PeriodStart,
            "periodEnd"    : PeriodEnd
            }

    def __iter__(self):
        return iter(self.resources)

    def __getitem__(self, item):
        return self.resources[item]

    def getTime(self):
        dt = datetime.utcnow()
        current = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        ceil_datetime = self.ceil_dt(current)
        start =  (ceil_datetime - timedelta(hours=1, minutes=30)).strftime("%Y%m%d%H%M")
        #end =    (ceil_datetime - timedelta(hours=1, minutes= 30) + timedelta(minutes=15)).strftime("%Y%m%d%H%M")
        end = ceil_datetime.strftime("%Y%m%d%H%M")

        print(end, start)
        return start, end

    def ceil_dt(self, dt):
        #how many secs have passed this hour
        nsecs = dt.minute * 60
        # number of seconds to next quarter hour mark
        delta = math.ceil(nsecs / 900) * 900 - nsecs
        return dt + timedelta(seconds=delta)