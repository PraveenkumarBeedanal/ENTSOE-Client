"""
Entry point App
"""
from argparse import ArgumentParser
from configparser import ConfigParser, NoSectionError, NoOptionError

from source.config import BaseConfig, FirebaseConfig, EntsoeConfig
from source.service import Firebase, Entsoe
import schedule
import time


def cfg_arg():
    """ add config argument to app
    :return: value of config
    """
    psr = ArgumentParser(description="Application")
    # add config argument
    psr.add_argument("config", type=str, help="Configuration details")

    # parse arguments
    args = psr.parse_args()

    # return value of config
    return args.config


def start():
    cfg_file = cfg_arg()
    cfg = BaseConfig(cfg_file, ConfigParser())

    try:
        # read config file
        cfg.read()
        entsoe = Entsoe(EntsoeConfig(cfg))
        entsoe.setup()
        rl_db = Firebase(FirebaseConfig(cfg)).realtime_database()
        print(rl_db.post("resources", entsoe.resources()))
        print(rl_db.post("emission_factor", entsoe.emission_factor()))

    except (FileNotFoundError, NoSectionError, NoOptionError) as e:
        print(e)
        raise SystemExit(1)


if __name__ == '__main__':

    schedule.every(15).minutes.do(start)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt as ki:
            print("exiting the application")
            break

