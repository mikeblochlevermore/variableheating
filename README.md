# Variable Heating

[See the Video](https://youtu.be/aNyE0nEGONs)<br>
[Try the app](https://variableheating.vercel.app/)

## We spent all our money on a Kronoterm heatpump...
An electrical device that sources heat from the air and uses it to warm radiators and hot water.

🔥 This web app suggests a heating schedule that reduces the temperature (just a little) when the electricity prices are high.

⚡️ The app gets today's electricty prices from [elpriserligenu.dk](https://www.elprisenligenu.dk), plus, if it's after 13.00, the prices for tomorrow.

💶 Behind the scenes, the transport costs are added, factoring in winter or summer tarrifs, and the total costs are displayed.

🌱 Finally, the heating settings below are applied, to create a suggested schedule for the heatpump

🐍 Built with Python and Flask


## A bit about Danish electrical prices

Denmark has one of the highest costs of electricity in Europe.
As such, finding small ways to reduce consumption is highly beneficial!

For those who have variable electricity costs,
the price you pay is a combination of several fees:

- The pure cost of electricity (which I sourced from [elpriserligenu.dk](https://www.elprisenligenu.dk))
- The transport costs (determined by your electrical grid operator)
- The state tax
- Any additional costs from your electricity provider

⚡️ The pure cost is different for the east and west sides of Denmark (with "Storbæltsbroen" as the mid-point). I have chosen to currently fix the prices to the east half of Denmark (undskyld Jylland...)

⚡️ For transport costs, I have selected [Cerius](https://cerius.dk/priser-og-tariffer/tariffer-og-netabonnement/) (my local grid owner).
As of Jan 2023, transport costs now have fixed values, divided into 3 periods of the day:
- low load: 00.00-06.00
- high load: 06.00-17.00 and 21.00-24.00
- peak load: 17.00-21.00
The values for these loads change depending on whether it's summer or winter.

⚡️ The state tax is reduced significantly for households who use over 4000kWh per year (i.e. heatpump owners), and so I have chosen to ignore this factor.

⚡️ Although you can't do anything to change the first three kinds of fees, each household can freely select their electricty provider who then have small fees for working out all the logisitcs of payments etc. If you choose well, these fees should be fairly insignificant, so I've also factored them out.

**TL;DR** - The app focusses on the pure costs of electricty and adds the transport costs.
This paints a clear enough picture to determine the fluxuations of price during the day.
After all, is a scheduling app, not necessarily a price-displaying app.


## A bit about the Kronoterm heatpump

Central-heating water is pumped into an outside unit which sources warmth from the air and returns it to the radiator system in the house.

[See a brochure](https://kronoterm.com/wp-content/uploads/2019/06/Adapt_flyer_LR_2019_06_05_ENG-1.pdf?dwpfuha=1678187331)

Approximately once every 24 hours, it will also warm up hot water for the taps and shower / bath, which it stores inside in a 200L tank.

The unit has in-built settings which allows you to schedule periods of reduced, normal and increased heating for the radiators, as well as when the hot water is heated.

However, this relies on manually deciding when to schedule these shifts - I wanted to base the decisions on when the electricity was cheaper, and whether or not one was at home.

## The Settings

🌱 ECO 🌀 NORMAL 👑 COMFORT 🚰 HOT WATER

Equivalent to slightly-reduced, normal, or slightly-increased central heating temperatures.
Plus a time to heat hot water.

The heatpump automatically shifts the temperature of the radiator water based on the outside temperatures.
The variable is based on a linear graph, created by setting the output temperatures of the unit when the outside temperatures are -15C and +15C respectively.
This sets the parameters for NORMAL operation.

However, you can additionally schedule periods of increased or reduced heating, which basically move the line of the graph up or down.

For instance, you might assign ECO mode to be a reduction of the general output temperature by -4C, and COMF mode to be an increase in temperature above the normal range of +5C.

Once you've set your normal operating temperature graph and your ECO and COMF settings, you can then schedule which periods you'd like increased, normal or reduced heating.

All of these operations can be set in the Kronoterm app (web and mobile) as well as on a diplay on the indoors unit itself.

This app suggests a daily schedule for ECO, NORMAL and COMF settings based on the electricity prices.

### Settings for a day at work

NIGHT TIME <br>
00.00 - 05.59 and 22.00 - 24.00 <br>
🌀 in general <br>
🌱 for prices over 1.5kr <br>
<br>
MORNING COFFEE <br>
06.00 - 07.59 <br>
👑 in general <br>
🌀 for prices over 2kr <br>
<br>
DAY TIME <br>
08.00 - 16.59 <br>
🌀 in general <br>
🌱 for prices over 1.5kr <br>
<br>
EVENING <br>
17.00 - 21.59 <br>
👑 in general <br>
🌀 for prices over 2kr <br>
🌱 for prices over 4kr <br>

### Settings for a day at home

 NIGHT TIME <br>
00.00 - 06.59 and 22.00 - 24.00 <br>
🌀 in general <br>
🌱 for prices over 1.5kr <br>
<br>
DAY TIME <br>
07.00 - 21.59 <br>
👑 in general <br>
🌀 for prices over 2kr <br>
🌱 for prices over 4kr <br>

### Settings for heating hot water

🚰 Water heating suggested on the cheapest hour between 00.00 and 06.59

# The Code

## Looking up the pure electricity prices
### get_today()
This function look's up today's date, the values of which can then be placed in the url for elprisenligenu.dk which returns a json file.

(Note that "DK2" in the url indicates prices for the East of Denmark, alternatively "DK1" would give the West.)

After storing these values in a list, the get_trans() function is called to add the transport costs.
The current month is required since the transport costs have winter and summer periods.

### get_tomo()
A near-identical function is included for getting the prices for the next day (if available). Typically the prices for the next day are published after 13.00

```
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
```

## Adding the transport costs
The get_trans() function creates a list called transport, which stores the hourly fees for transport.

```
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
```

## Getting the settings

### work = 0
In index.html there's a toggle button to set the schedule for a day at work (which typically has lower temperatures set, since you'd be out of the house).

Clicking the button sends the app through the /work route, which sets the "work" value to 1, otherwise for a day at home "work" = 0. (Further down this function is a scenario for if work = 1).

### get_settings()
This function looks at the totals_today (pure cost + transport), lists of the costs of each each hour, and assigns a setting based on whether one is at home or not, and what hour it is.

The results are stored in a list called settings_today

### An near-identical fuction exists for calculating the settings for the next day
Which works with totals_tomo and outputs: settings_tomo

```
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
```

## Displaying the prices

In index.html (plus the equivalent for a day at work: work.html), the prices are displayed by creating bars in a table.
The bar width is determined by the total prices (multiplied by 60 for aesthetics).
The bar is also labelled with the total prices.
Using if-statements, the bar colour is determined by the price: red for prices over 2.0kr, yellow for over 1.2kr and otherwise, green.

```
{% for i in range(24) %}
    <td class="bars">
        {% if totals_today[i]|float > 2.0 %}
            <div class="bar-red" style="width:{{ totals_today[i] * 60}}%;">{{ totals_today[i] }}kr</div>
        {% elif totals_today[i]|float > 1.2 %}
            <div class="bar-yellow" style="width:{{ totals_today[i] * 60}}%;">{{ totals_today[i] }}kr</div>
        {% else %}
            <div class="bar-green" style="width:{{ totals_today[i] * 60}}%;">{{ totals_today[i] }}kr</div>
        {% endif %}
    </td>
{% endfor %}
```

## Displaying the settings
The settings_today list contains string values "ECO", "NORM" or "COMF", which this changes into emojis.

There is also a simple function in the backend to work out the cheapest time (between 00:00 and 06:59), which will be assigned to hot water heating - indicated by the tap emoji. The cheapest_today value will be an integer between 0 and 23, so it can be easily compared to the hour as they are cycled through in the for loop.

```
{% for i in range(24) %}
    <tr class="table">
        <td class="comment">
            {% if i == cheapest_today %} 🚰 {% endif %}
            {% if settings_today[i] == "ECO" %} 🌱
            {% elif settings_today[i] == "NORM" %} 🌀
            {% elif settings_today[i] == "COMF" %} 👑
            {% endif %}
        </td>
{% endfor %}
```

# Details
Created March 2023<br>
Mike Bloch-Levermore<br>
interactivephilosophy@gmail.com<br>
As a final project for Harvard's introduction to Computer Science: [CS50x](https://www.edx.org/course/introduction-computer-science-harvardx-cs50x?utm_source=google&utm_campaign=19315581336&utm_medium=cpc&utm_term=edx%20cs50%20course&hsa_acc=7245054034&hsa_cam=19315581336&hsa_grp=144242542763&hsa_ad=642052609434&hsa_src=g&hsa_tgt=kwd-757305580526&hsa_kw=edx%20cs50%20course&hsa_mt=e&hsa_net=adwords&hsa_ver=3&gclid=CjwKCAiA3pugBhAwEiwAWFzwdaZwaNXy5wsyziuZnk_J5tINeEw85Jo-RRx3_6yzD0-6Tb7w_2dNAxoCa8sQAvD_BwE)
