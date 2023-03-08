from urllib.request import urlopen
from datetime import date, timedelta, datetime
from flask import Flask, render_template, request
import json
import urllib.error

app = Flask(__name__)

@app.route("/")
def index():

    totals_today = get_today()
    cheapest_today = get_cheapest_today(totals_today)

    # gets settings for a day at home
    work = 0
    settings_today = get_settings(totals_today, work)

    # if the time if after 13, get tomorrow's totals

    now = datetime.now()
    hour = int(now.strftime("%H"))

    if hour >= 13:
        totals_tomo = get_tomo()
        cheapest_tomo = get_cheapest_tomo(totals_tomo)

        # gets settings for a day at home
        work = 0
        settings_tomo = get_settings_tomo(totals_tomo, work)
    else:
        totals_tomo = 0
        settings_tomo = None
        cheapest_tomo = None

    return render_template("index.html", settings_tomo=settings_tomo, cheapest_today=cheapest_today, settings_today=settings_today, cheapest_tomo=cheapest_tomo, totals_tomo=totals_tomo, totals_today=totals_today)


def get_today():

    # Looks up today's date
    today = date.today()

    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    # Sends the date into the url to get json file
    url = "https://www.elprisenligenu.dk/api/v1/prices/{}/{}-{}_DK2.json".format(year, month, day)

    # stores the response of URL
    response = urlopen(url)

    # storing the JSON response
    data = json.loads(response.read())

    # stores the prices for each hour in a list "prices[0 - 23]"
    prices_today = []
    for i in range(24):
        prices_today.append(data[i]["DKK_per_kWh"])

    transport = get_trans(int(month))

    # adds transport costs to prices
    totals_today = []
    for i in range(24):
        totals_today.append(prices_today[i] + transport[i])
        totals_today[i] = round(totals_today[i], 2)

    return totals_today


def get_tomo():

    # Looks up tomorrow's date
    tomorrow = date.today() + timedelta(days=1)

    year = tomorrow.strftime("%Y")
    month = tomorrow.strftime("%m")
    day = tomorrow.strftime("%d")

    # Sends the date into the url to get json file
    url = "https://www.elprisenligenu.dk/api/v1/prices/{}/{}-{}_DK2.json".format(year, month, day)

    # stores the response of URL
    try:
        response = urlopen(url)
        http = 0
    except urllib.error.HTTPError:
        http = 1

    if http != 1:

        # storing the JSON response
        data = json.loads(response.read())

        # stores the prices for each hour in a list "prices[0 - 23]"
        prices_tomo = []
        for i in range(24):
            prices_tomo.append(data[i]["DKK_per_kWh"])

        transport = get_trans(int(month))

        # adds transport costs to prices
        totals_tomo = []
        for i in range(24):
            totals_tomo.append(prices_tomo[i] + transport[i])
            totals_tomo[i] = round(totals_tomo[i], 2)

        return totals_tomo

    else:
        totals_tomo = 1
        return totals_tomo


def get_trans(month):
    # adds the transport costs of electricity to a list
    # works by adding prices to the end of the list, so they're ordered

    transport = []

    if month > 9 or month < 4:
        # for winter tariff (oct-mar)
        for i in range(6):
            transport.insert(len(transport), 0.1772)

        for i in range(11):
            transport.insert(len(transport), 0.5334)

        for i in range(4):
            transport.insert(len(transport), 1.6003)

        for i in range(3):
            transport.insert(len(transport), 0.1772)

        return transport

    else:
        # for summer tariff (apr-sept)
        for i in range(6):
            transport.insert(len(transport), 0.1772)

        for i in range(11):
            transport.insert(len(transport), 0.2668)

        for i in range(4):
            transport.insert(len(transport), 0.6935)

        for i in range(3):
            transport.insert(len(transport), 0.1772)

        return transport

def get_cheapest_today(totals_today):

    # selects cheapest time between 00:00 and 06:00

    cheapest_today = min(totals_today[:6])

    for i in range(6):
        if cheapest_today == totals_today[i]:
            cheapest_today = i

    return cheapest_today

def get_cheapest_tomo(totals_tomo):

    # selects cheapest time between 00:00 and 06:00

    cheapest_tomo = min(totals_tomo[:6])

    for i in range(6):
        if cheapest_tomo == totals_tomo[i]:
            cheapest_tomo = i

    return cheapest_tomo


def get_settings(totals_today, work):

    # system has 3 settings: Eco, Normal and Comfort
    # Equalling reduced, normal or increased heating / power consumption

    settings_today = []

    if work == 0:


 #SETTINGS FOR DAY AT HOME
    # If during the day:
    # set comfort, unless medium cost, then set normal
    # if high costs, set eco, but only for 2 hours at a time

    # If during night, set normal, unless high cost

        for i in range(24):
            # assign settings from 00.00 to 06.59
            if i >= 0 and i < 7:
                if totals_today[i] > 1.5:
                    settings_today.insert(len(settings_today), "ECO")
                else:
                    settings_today.insert(len(settings_today), "NORM")
            # assign settings from 07.00 to 21.59
            elif i >= 7 and i < 22:
                if totals_today[i] > 4.0:
                    settings_today.insert(len(settings_today), "ECO")
                elif totals_today[i] > 2.0:
                    settings_today.insert(len(settings_today), "NORM")
                else:
                    settings_today.insert(len(settings_today), "COMF")
            # assign settings from 22.00 to 24.00
            else:
                if totals_today[i] > 1.5:
                    settings_today.insert(len(settings_today), "ECO")
                else:
                    settings_today.insert(len(settings_today), "NORM")

        return settings_today

    else:

#SETTINGS FOR DAY AT WORK

    # During night, set normal, unless high cost, then eco

        for i in range(24):
            # 00.00 - 05.59
            if i >= 0 and i < 6:
                if totals_today[i] > 1.5:
                    settings_today.insert(len(settings_today), "ECO")
                else:
                    settings_today.insert(len(settings_today), "NORM")

            # 06.00 - 07.59:
            # set comf, unless medium cost, then set norm
            elif i >= 6 and i < 8:
                if totals_today[i] > 2.0:
                    settings_today.insert(len(settings_today), "NORM")
                else:
                    settings_today.insert(len(settings_today), "COMF")

            # 08.00 - 16.59:
            # set normal, unless medium cost, then set eco
            elif i >= 8 and i < 17:
                if totals_today[i] > 1.5:
                    settings_today.insert(len(settings_today), "ECO")
                else:
                    settings_today.insert(len(settings_today), "NORM")

            # 17.00 - 21.59
            # set comfort, unless medium cost, then set normal
            # if high costs, set eco
            elif i >= 17 and i < 22:
                if totals_today[i] > 4.0:
                    settings_today.insert(len(settings_today), "ECO")
                elif totals_today[i] > 2.0:
                    settings_today.insert(len(settings_today), "NORM")
                else:
                    settings_today.insert(len(settings_today), "COMF")
            # 22.00 - 24.00
            else:
                if totals_today[i] > 1.5:
                    settings_today.insert(len(settings_today), "ECO")
                else:
                    settings_today.insert(len(settings_today), "NORM")

        return settings_today

def get_settings_tomo(totals_tomo, work):

    # system has 3 settings: Eco, Normal and Comfort
    # Equalling reduced, normal or increased heating / power consumption

    settings_tomo = []

    if work == 0:

 #SETTINGS FOR DAY AT HOME
    # If during the day:
    # set comfort, unless medium cost, then set normal
    # if high costs, set eco, but only for 2 hours at a time

    # If during night, set normal, unless high cost

        for i in range(24):
            # 00.00 to 06.59
            if i >= 0 and i < 7:
                if totals_tomo[i] > 1.5:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                else:
                    settings_tomo.insert(len(settings_tomo), "NORM")
            # 07.00 to 21.59
            elif i >= 7 and i < 22:
                if totals_tomo[i] > 4.0:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                elif totals_tomo[i] > 2.0:
                    settings_tomo.insert(len(settings_tomo), "NORM")
                else:
                    settings_tomo.insert(len(settings_tomo), "COMF")
            # 22.00 to 24.00
            else:
                if totals_tomo[i] > 1.5:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                else:
                    settings_tomo.insert(len(settings_tomo), "NORM")

        return settings_tomo

    else:

# SETTINGS FOR DAY AT WORK

    # During night, set normal, unless high cost, then eco

        for i in range(24):
            # 00.00 - 05.59
            if i >= 0 and i < 6:
                if totals_tomo[i] > 1.5:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                else:
                    settings_tomo.insert(len(settings_tomo), "NORM")

            # 06.00 - 07.59:
            # set comf, unless medium cost, then set norm
            elif i >= 6 and i < 8:
                if totals_tomo[i] > 2.0:
                    settings_tomo.insert(len(settings_tomo), "NORM")
                else:
                    settings_tomo.insert(len(settings_tomo), "COMF")

            # 08.00 - 16.59:
            # set normal, unless medium cost, then set eco
            elif i >= 8 and i < 17:
                if totals_tomo[i] > 1.5:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                else:
                    settings_tomo.insert(len(settings_tomo), "NORM")

            # 17.00-21.59
            # set comfort, unless medium cost, then set normal
            # if high costs, set eco
            elif i >= 17 and i < 22:
                if totals_tomo[i] > 4.0:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                elif totals_tomo[i] > 2.0:
                    settings_tomo.insert(len(settings_tomo), "NORM")
                else:
                    settings_tomo.insert(len(settings_tomo), "COMF")

            # 22.00-24.00
            else:
                if totals_tomo[i] > 1.5:
                    settings_tomo.insert(len(settings_tomo), "ECO")
                else:
                    settings_tomo.insert(len(settings_tomo), "NORM")

        return settings_tomo


@app.route("/about")
def about():

    return render_template("about.html")


@app.route("/work")
def work():

    totals_today = get_today()
    cheapest_today = get_cheapest_today(totals_today)

    # gets settings for a day at work
    work = 1
    settings_today = get_settings(totals_today, work)

    # if the time if after 13, get tomorrow's totals

    now = datetime.now()
    hour = int(now.strftime("%H"))

    if hour >= 13:
        totals_tomo = get_tomo()
        cheapest_tomo = get_cheapest_tomo(totals_tomo)

        # gets settings for a day at work
        work = 1
        settings_tomo = get_settings_tomo(totals_tomo, work)
    else:
        totals_tomo = 0
        settings_tomo = None
        cheapest_tomo = None


    return render_template("work.html", settings_tomo=settings_tomo, cheapest_today=cheapest_today, settings_today=settings_today, cheapest_tomo=cheapest_tomo, totals_tomo=totals_tomo, totals_today=totals_today)

