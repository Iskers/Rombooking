import sys
import re
import datetime
import calendar
import configparser
import requests_driver
import site_model


# --------------- Settings ---------------

def date_generator(config_parser: configparser.ConfigParser):
    dates_number = int(config["Time"]["dates_number"])
    #if int(config["Time"]["advance"]) + dates_number > 14:
    #    raise Exception("Mer enn 14 dager fremover i bestillingen")

    if config["Time"]["current_time"] == "true":
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        start_date = now.day + int(config["Time"]["advance"])
        current_month_length = calendar.monthrange(year, month)[1]
        # todo test på denne
        if current_month_length < start_date:
            if month == 12:
                month = 1
            else:
                month = month + 1
            start_date = start_date - current_month_length
    else:
        raise Exception("Dette er ikke konfigurert")
    # todo, denne er ikke i orden fordi year-month-sec ikke stemmer når en tar for seg en config. metoden er tatt ut
    # så den stemmer vel.
    dates = []
    sec = start_date - 1
    for i in range(dates_number):
        sec = sec + 1
        #Todo test av denne. Den er kjapt snekret sammen.
        if sec > current_month_length:
            sec = 1
            month += 1
        day_string = control_if_zeroed(sec)
        month_string = control_if_zeroed(month)
        date = f"{year}-{month_string}-{day_string}"
        dates.append(date)
    return dates


def ios_date_generator(dater, number_days):
    # Format : 2021-03-15T08:00:00+01:00
    date = datetime.datetime.strptime(dater, "%Y-%m-%dT%H:%M:%S%z")
    times = [dater[11:16]]
    dates = []
    for i in range(number_days):
        date += datetime.timedelta(days=1)
        dates.append(date.isoformat()[:10])
    return dates, times


def ios_duration_generator(dur):
    numbers = re.findall(r'\b([1-9]|[0-9][0-9])\b', dur)
    hours = int(numbers[0])
    hours = control_if_zeroed(hours)
    if len(dur) > 10:
        minutes = int(numbers[1])
        minutes = control_if_zeroed(minutes)
    else:
        minutes = "00"
    return f"{hours}:{minutes}"


def control_if_zeroed(number):
    if number < 10:
        return f"0{number}"
    else:
        return number


# --------------- Run ---------------
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('App.config')

    room = site_model.Room.create_from_config(config)
    website = site_model.Website.create_from_config(config)

    responses = []
    failed_responses = []

    logger = requests_driver.Logger()

    # --------------- Config ---------------
    if sys.platform == "ios":
        args = sys.argv
        user = site_model.User(args[1], args[2])
        room.seat = args[8]
        dates, times = ios_date_generator(args[5], int(args[7]))
        duration = ios_duration_generator(args[6])
        order_template = site_model.Order_template(args[3], args[4], room, website, user)

    elif sys.platform in ("darwin", "win32", "linux"):
        user = site_model.User.create_from_config(config)
        room.seat = 1
        dates = date_generator(config)
        times = config["From"]
        duration = config["Time"]["duration"]
        order_template = site_model.Order_template.create_from_config(config, room=room, website=website, user=user)
    else:
        raise Exception("Not configured for your OS")
    prim_seat = room.seat

    requests_handler = requests_driver.Web_Handler(website, user)
    requests_handler.csrf_generation(order_template)

    for date in dates:
        for key in times:
            if sys.platform == "ios":
                order = site_model.Order(order_template, key, duration, date)
            else:
                order = site_model.Order(order_template, times[key], duration, date)
            response = requests_handler.book_room(order)
            logger.log_order_response(order, response)
            # TODO hele denne kan egentlig tas bort, bugs er i orden.
            try:
                requests_handler.response_control(response)
            except:
                failed_responses.append(response)
                print(f"{date} with seat {room.seat} is booked, trying random seat")
                order.room.seat = 0
                response = requests_handler.book_room(order)
                logger.log_order_response(order, response)
                try:
                    requests_handler.response_control(response)
                except:
                    print(f"{date} can not be booked.")

            finally:
                order.room.seat = prim_seat
            responses.append(response)

    logger.save_logs()
    if len(failed_responses):
        print(len(failed_responses))
