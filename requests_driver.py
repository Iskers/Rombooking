import requests
from multiprocessing import Queue
import re
import site_model
import datetime
import json


class Web_Handler:
    def __init__(self, website: site_model.Website, user: site_model.User):
        self._session = requests.session()
        self.website = website
        self.user = user
        self._initiate_connection()

    def _initiate_connection(self):
        # Login init
        init = self._session.get(self.website.base_url)
        auth = re.search(r"\?AuthState\S+", init.url).group()
        auth_uri = self.website.auth_url + auth + "&org=ntnu.no"

        # Login
        response = self._session.post(auth_uri, data=self.user.payload)
        if re.search("Innlogging feilet", response.text):
            raise Exception("Wrong password, or username")

        SAMLResponse = re.search(r'(?<="SAMLResponse" value=")(.*)(?=(">))', response.text).group()
        RelayState = re.search(r'(?<="RelayState" value=")(.*)(?=(">))', response.text).group()
        js_check_payload = {"SAMLResponse": f"{SAMLResponse}",
                            "RelayState": f"{RelayState}"}
        # JS block pass
        pass_js_check = self._session.post(self.website.second_auth_url,
                                           data=js_check_payload)

    def book_room(self, order: site_model.Order):
        response = self._session.post(self.website.base_url, order.order_payload)
        # TODO Hva gjør denne?
        if True:
            pass
        return response

    def csrf_generation(self, order_template: site_model.Order_template):
        # Csrf Token only needed once. In order to skip, create day dict for lookup
        response = self._session.post(self.website.base_url, data=order_template.csrf_payload)
        order_template.csrftoken = re.search('(?<="csrftoken" value=")(.*)(?=")', response.text).group()
        return order_template

    @staticmethod
    def format_time(time):
        start_hour = time[:2]
        start_minutes = time[2:]
        return f"{start_hour}:{start_minutes}"

    @staticmethod
    def format_date(date: str):
        return f"{date[6:]}-{date[3:5]}-{date[:2]}"

    @staticmethod
    def response_control(response):
        control = re.findall("var allerede bestilt", response.text)
        if len(control) != 0:
            raise Exception("Bestilling allerede utført")
        else:
            return


class Logger:
    def __init__(self):
        self._date = datetime.datetime.now()
        self._logs = []
        self._responses = []
        self._orders = []

    def log_order_response(self, order, response):
        log = json.dumps(order.order_payload) + "\n" + response.text
        self._logs.append(log)

    def log_order(self, order):
        self._orders.append(order)

    def log_response(self, response):
        self._responses.append(response)

    def load_logs(self):
        pass

    def save_logs(self):
        file = open(f"Logs/{self._date}.txt", "w")
        try:
            for log in self._logs:
                file.write(log)
                file.write("\n\n")
                file.write(f"-------------------------------------NEW ORDER-------------------------------------\n")
        except:
            return 0
        finally:
            file.close()
            return 1


'''
class Web_Handler:
    _standard_payload = {
        "reservation_type": "single_place",
        "roomtype": "NONE",
        "size": "1",
        "single_place": "on",
    }

    def __init__(self, base_uri, user: User):
        self._session = requests.session()
        self._base_uri = base_uri.base_url
        self._initiate_connection(user.payload)

    def _initiate_connection(self, payload: dict):
        # Login init
        init = self._session.get(self._base_uri)
        auth = re.search("\?AuthState\S+", init.url).group()
        auth_uri = "https://idp.feide.no/simplesaml/module.php/feide/login" + auth + "&org=ntnu.no"

        # Login
        response = self._session.post(auth_uri, data=payload)
        if re.search("Innlogging feilet", response.text):
            raise Exception("Wrong password, or username")

        SAMLResponse = re.search('(?<="SAMLResponse" value=")(.*)(?=(">))', response.text).group()
        RelayState = re.search('(?<="RelayState" value=")(.*)(?=(">))', response.text).group()
        js_check_payload = {"SAMLResponse": f"{SAMLResponse}",
                            "RelayState": f"{RelayState}"}
        # JS block pass
        pass_js_check = self._session.post("https://tp.uio.no/simplesaml/module.php/saml/sp/saml2-acs.php/feide-sp",
                                           data=js_check_payload)

    def book_room(self, start, duration, date, room_id, seat, description, notes):
        # Initial payload creation
        order_payload = {"start": start,
                         "duration": duration,
                         "preset_date": date,
                         "room[]": room_id,
                         "submitall": "Bestill+⇨"
                         }
        order_payload.update(self._standard_payload)
        # Run through the csrt token gen
        order_payload.update(self._csrf_generation(payload=order_payload))
        # Remove excess info from token gen
        order_payload.pop("submitall")
        order_payload["placenr"] = seat
        order_payload["name"] = description
        order_payload["notes"] = notes
        order_payload["confirmed"] = "true"
        # todo add some acceptance step? / raise
        response = self._session.post(self._base_uri, order_payload)
        if True:
            pass
        return response

    def _csrf_generation(self, payload: dict):
        # Csrf Token only needed once. In order to skip, create day dict for lookup
        response = self._session.post(self._base_uri, data=payload)
        csrftoken = re.search('(?<="csrftoken" value=")(.*)(?=")', response.text).group()
        dates = re.search('(?<="dates\[]" value=")(.*)(?=")', response.text).group()
        preset_day = re.search('(?<="preset_day" value=")(.*)(?=")', response.text).group()
        preset_date = re.search('(?<="preset_date" value=")(.*)(?=")', response.text).group()
        return {"dates[]": dates,
                "preset_date": preset_date,
                "preset_day": preset_day,
                "csrftoken": csrftoken}

    @staticmethod
    def format_time(time):
        start_hour = time[:2]
        start_minutes = time[2:]
        return f"{start_hour}:{start_minutes}"

    @staticmethod
    def format_date(date: str):
        return f"{date[6:]}-{date[3:5]}-{date[:2]}"
'''

'''
    final_payload = {
        "placenr": "1",
        "name": "Plassbestillinger",
        "notes": "skolearbeid",
        "confirmed": "true",
        "dates[]": dates,
        "preset_date": preset_date,
        "preset_day": preset_day,
        "csrftoken": csrftoken
    }
    final_payload.update(payload)
    final_payload.pop("submitall")
    final_payload.pop("full_day")
    final_response = s.post(rombestilling_uri, data=final_payload)
    return final_response

order_payload = {"start": "08:00",
                 "duration": "04:00",
                 "preset_date": "2020-12-18",
                 "single_place": "on",
                 "employee_as_student": "",
                 "room[]": "306470",
                 "size": "1",
                 "submitall": "Bestill+⇨",
                 "exam": "",
                 "full_day": "false",
                 "roomtype": "NONE",
                 "area": "",
                 "building": ""
                 }
'''
