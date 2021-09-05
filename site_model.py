# import requests_driver
# import configparser
from datetime import datetime
import getpass


class Website:
    def __init__(self, base_url, auth_url=None, second_auth_url=None):
        self._base_url = base_url
        self._auth_url = auth_url
        self._second_auth_url = second_auth_url

    @property
    def base_url(self):
        return self._base_url

    @property
    def auth_url(self):
        return self._auth_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    @auth_url.setter
    def auth_url(self, value):
        self._auth_url = value

    @property
    def second_auth_url(self):
        return self._second_auth_url

    @second_auth_url.setter
    def second_auth_url(self, value):
        self._second_auth_url = value

    @classmethod
    def create_from_config(cls, config_parser):
        base_url = config_parser['Website']['base_url']
        auth_url = config_parser['Website']['auth_url']
        second_auth_url = config_parser['Website']['auth_second_url']
        return cls(base_url, auth_url, second_auth_url)


class User:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self.payload = {
            "feidename": username,
            "password": password,
            "inside_iframe": "0",
            "has_js": "0"
        }

    @classmethod
    def create_from_config(cls, config_parser):
        username = config_parser['User']['username']
        password = bool(config_parser['User']['password'])
        if password:
            password = config_parser['User']['password']
        else:
            password = getpass.getpass()
        return cls(username, password)


class Room:
    def __init__(self, room_id, seat=1, room_number: int = None, building=None):
        self._building = building
        self._room_number = room_number
        self._seat = seat
        self._room_id = room_id

    @property
    def building(self):
        return self._building

    @building.setter
    def building(self, value):
        self._building = value

    @property
    def room_number(self):
        return self._room_number

    @room_number.setter
    def room_number(self, value):
        self._room_number = value

    @property
    def seat(self):
        return self._seat

    @seat.setter
    def seat(self, value):
        self._seat = value

    @property
    def room_id(self):
        return self._room_id

    @room_id.setter
    def room_id(self, value):
        self._room_id = value

    @classmethod
    def create_from_config(cls, config_parser):
        building = config_parser["Room"]["building"]
        room_number = config_parser["Room"]["room_number"]
        seat = config_parser['Room']['seat']
        room_id = config_parser["Room"]["room_id"]
        return cls(room_id, seat, room_number, building)


class Order_template:
    _standard_payload = {
        "reservation_type": "single_place",
        "roomtype": "NONE",
        "size": "1",
        "single_place": "on",
    }

    def __init__(self, description, notes, room: Room, website: Website, user: User):
        self._description = description
        self._notes = notes
        self._room = room
        self._website = website
        self._user = user
        self._csrftoken = None

    @property
    def payload(self) -> dict:
        payload = {
            "start": "08:00",
            "duration": "01:00",
            "preset_date": str(datetime.now())[:10],
            "room[]": self._room.room_id
        }
        payload.update(self._standard_payload)
        return payload

    @property
    def csrf_payload(self) -> dict:
        payload = {"submitall": "Bestill+⇨"}
        payload.update(self.payload)
        return payload

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

    @property
    def csrftoken(self):
        return self._csrftoken

    @csrftoken.setter
    def csrftoken(self, value):
        self._csrftoken = value

    @classmethod
    def create_from_config(cls, config_parser, **kwargs):
        description = config_parser["Info"]["description"]
        notes = config_parser["Info"]["note"]
        return cls(description, notes, **kwargs)


class Order(Order_template):
    _preset_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    def __init__(self, order_template: Order_template, start, duration, date):
        super(Order, self).__init__(order_template._description, order_template._notes, order_template._room,
                                    order_template._website, order_template._user)
        self._parent = order_template
        self._start = start
        self._duration = duration
        self._date = date
        self.preset_day = self._preset_days[datetime.strptime(date, "%Y-%m-%d").weekday()]

    @property
    def date(self):
        return self._date

    @property
    def room(self):
        if self._room:
            return self._room
        else:
            return None

    @room.setter
    def room(self, value):
        self._room = value

    @property
    def csrftoken(self):
        return self._parent.csrftoken

    @csrftoken.setter
    def csrftoken(self, value):
        self._parent.csrftoken = value

    @property
    def payload(self) -> dict:
        payload = {
            "start": self._start,
            "duration": self._duration,
            "preset_date": self.date,
            "room[]": self._room.room_id
        }
        payload.update(self._standard_payload)
        return payload

    @property
    def csrf_payload(self) -> dict:
        payload = {"submitall": "Bestill+⇨"}
        payload.update(self.payload)
        return payload

    @property
    def order_payload(self) -> dict:
        payload = {
            "placenr": self._room.seat,
            "name": self.description,
            "notes": self.notes,
            "confirmed": "true",
            "dates[]": self.date,
            "preset_day": self.preset_day,
            "csrftoken": self.csrftoken
        }
        payload.update(self.payload)
        return payload
