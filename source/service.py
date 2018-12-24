"""
Firebase services

"""

import json
from bs4 import BeautifulSoup
import dateutil.parser as dp
from datetime import datetime, timedelta
from socket import gaierror

import requests


class Firebase:
    """class that provides firebase services
    """

    def __init__(self, fb_cfg):
        self.database_url = fb_cfg.database_url

    def __str__(self):
        return "Connection to firebase services"

    def realtime_database(self):
        return RealtimeDatabase(self.database_url)


class RealtimeDatabase:
    """class the perform REST API calls to Realtime database
    """

    def __init__(self, database_url):
        self.database_url = database_url
        self.path = ""

    def _check_token(self):
        return f"{self.database_url}{self.path}.json"

    def post(self, path, data):
        self.path = path
        response = requests.post(self._check_token(), data=data)
        return response.json()


PSR_TYPES = {
    'B01': ['Biomass', 18],
    'B02': ['Fossil Brown coal', 1001],
    'B03': ['Fossil Coal Gas', 469],
    'B04': ['Fossil Gas', 469],
    'B05': ['Fossil Hard coal', 1001],
    'B06': ['Fossil oil', 840],
    'B09': ['Geothermal', 45],
    'B10': ['Hydro Storage', 5],
    'B11': ['Hydro Poundage', 5],
    'B12': ['Hydro Reserviour', 5],
    # 'B13': ['Marine', 8],
    'B14': ['Nuclear', 16],
    'B15': ['Other Renewable', 700],
    'B16': ['Solar', 46],
    'B17': ['waste', 700],
    'B18': ['Wind offshore', 12],
    'B19': ['Wind Onshore', 12],
    'B20': ['Other', 700]
    }


class Entsoe:

    def __init__(self, entsoe_cfg):
        self.cfg = entsoe_cfg

        self.endpoint = self.cfg.endpoint
        self.params = self.cfg.params
        self.periodStart = self.params.get("periodStart")
        self.data = {}
        self.sum_ef = 0
        self.sum_quantity = 0
        self.co2 = 0
        self.quantity = 0

    def setup(self):
        # loop over all resources
        flag = True;
        flag1 = False;
        for res in self.cfg:
            # set url psrType
            self.params["psrType"] = res


            try:

                # self.quantity = float(BeautifulSoup(requests.get(self.endpoint, params=self.params).text,
                #                            "html.parser").find("quantity").text)
                response_url = requests.get(self.endpoint, params=self.params)
                print(response_url.url)
                response = response_url.text
                soup = BeautifulSoup(response, "html.parser")
                parsed_t = dp.parse(soup.find("timeseries").find("period").find("end").text)
                periodEnd = parsed_t.strftime("%Y%m%d%H%M")
                print("the scraped periodEnd for ", res, "is", periodEnd)
                all_quantity = soup.find("timeseries").find("period").findAll("quantity")


                #lets keep it 7:45 , because utc time(9.15) - 1.5 hours
                copy_periodStart = datetime.strptime(self.params.get("periodStart"),"%Y%m%d%H%M")

                while flag1:
                    #if periodstart set to actual periond start set by us
                    if self.periodStart == copy_periodStart.strftime("%Y%m%d%H%M"):
                        self.quantity = float(all_quantity[0].getText())
                        break

                    # if periodstart set 15min after actual period start
                    elif self.periodStart == (copy_periodStart +timedelta(minutes= 15)).strftime("%Y%m%d%H%M"):
                        if self.periodStart == periodEnd:
                            self.quantity = float(all_quantity[0].getText())
                            break
                        else:
                            self.quantity = float(all_quantity[1].getText())
                            break

                    # if periodstart set 30min after actual period start
                    elif self.periodStart == (copy_periodStart +timedelta(minutes= 30)).strftime("%Y%m%d%H%M"):
                        if self.periodStart == periodEnd:
                            self.quantity = float(all_quantity[1].getText())
                            break
                        else:
                            self.quantity = float(all_quantity[2].getText())
                            break

                    # if periodstart set 45min after actual period start
                    elif self.periodStart == (copy_periodStart +timedelta(minutes= 45)).strftime("%Y%m%d%H%M"):
                        if self.periodStart == periodEnd:
                            self.quantity = float(all_quantity[2].getText())
                            break
                        else:
                            self.quantity = float(all_quantity[3].getText())
                            break

                    # if periodstart set 1hour after actual period start
                    elif self.periodStart == (copy_periodStart + timedelta(hours=1)).strftime("%Y%m%d%H%M"):
                        if self.periodStart == periodEnd:
                            self.quantity = float(all_quantity[3].getText())
                            break
                        else:
                            self.quantity = float(all_quantity[4].getText())
                            break
                    # if periodstart set 1 hour 15min after actual period start

                    else:
                        if self.periodStart == periodEnd:
                            self.quantity = float(all_quantity[4].getText())
                            break
                        else:
                            self.quantity = float(all_quantity[5].getText())
                            break

                while flag:
                    flag = False
                    flag1 = True
                    #7.45+ 15 = 8:00
                    if periodEnd == (copy_periodStart +timedelta(minutes= 15)).strftime("%Y%m%d%H%M"):
                        self.quantity = float(all_quantity[-1].getText())
                        self.periodStart = copy_periodStart.strftime("%Y%m%d%H%M")

                    # 7.45+ 30 = 8:30
                    elif periodEnd == (copy_periodStart +timedelta(minutes= 30)).strftime("%Y%m%d%H%M"):
                        self.quantity = float(all_quantity[-1].getText())
                        self.periodStart = (copy_periodStart + timedelta(minutes=15)).strftime("%Y%m%d%H%M")

                    # 7.45+ 45 = 8:15
                    elif periodEnd == (copy_periodStart +timedelta(minutes= 45)).strftime("%Y%m%d%H%M"):
                        self.quantity = float(all_quantity[-1].getText())
                        self.periodStart = (copy_periodStart + timedelta(minutes=30)).strftime("%Y%m%d%H%M")

                    # 7.45+ 1 hour = 8:45
                    elif periodEnd == (copy_periodStart +timedelta(hours=1)).strftime("%Y%m%d%H%M"):
                        self.quantity = float(all_quantity[-1].getText())
                        self.periodStart = (copy_periodStart + timedelta(minutes=45)).strftime("%Y%m%d%H%M")

                    # 7.45+ 1 hour and 15 min = 9:00
                    elif periodEnd == (copy_periodStart +timedelta(hours=1, minutes=15)).strftime("%Y%m%d%H%M"):
                        self.quantity = float(all_quantity[-1].getText())
                        self.periodStart = (copy_periodStart + timedelta(hours=1)).strftime("%Y%m%d%H%M")

                    else:
                        self.quantity = float(all_quantity[-1].getText())
                        self.periodStart = (copy_periodStart + timedelta(hours=1, minutes=15)).strftime("%Y%m%d%H%M")



            except IndexError:
                self.quantity = 0
                print("Errror occured while parsing the XML")

            except AttributeError:
                self.quantity = 0
                print("No attribute found for this resource")

            except (requests.ConnectionError, gaierror):
                self.quantity = 0
                print("Conection error occured")

            except requests.HTTPError:
                self.quantity = 0
                print("HTTP response error occured")



            res_ef = self.quantity * 0.25 * PSR_TYPES.get(res)[-1]
            self.sum_quantity += self.quantity
            self.sum_ef += res_ef
            self.data[res] = self.quantity

    def resources(self):
        res_data = {PSR_TYPES.get(key)[0]: val for key, val in self.data.items()}
        res_data.update({"periodStart": self.periodStart})
        print(res_data)
        # default UTF-8
        return json.dumps(res_data).encode()

    def calculate_co2(self):
        try:
            return self.sum_ef / (self.sum_quantity * 0.25)
        except ZeroDivisionError:
            print("There is no value for this time")

    def emission_factor(self):
        ef_data = {
            "co2"        : self.calculate_co2(),
            "periodStart": self.periodStart,
            "Electricity": self.sum_quantity
            }
        print(ef_data)
        return json.dumps(ef_data).encode()


