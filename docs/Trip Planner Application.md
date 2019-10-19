# Trip Planner Application

### Application Description

The intention of this project is to develop a python application that interacts with the New South Wales Government's Trip Planner API available on their open data platform. Users must be able to retrieve information about a stop including timetable information for departures at a given date / time as well as plan a trip from a given origin and destination. Information should include the time of arrival total fare cost and total duration of a journey. Users should also be able to save their favourite stop / platform or trip and be able to retrieve live updates about the latest departures and track work information affecting their trip.

### Proposed Solution

 The application infrastructure and communication endpoints should be handled by a Flask Server and a web browser for user interaction. The flask server will provide endpoints - `/stops`, `/departures`/<id>, `/trip`, `/trip/journeys`, etc - for users to retrieve information about requested stops / journeys and view them in HTML, using Flask's Jinja2 Templating Engine. By using an auto-generated Swagger client provided by the open data platform, our application can appropriately handle any request and response  to/ from the API and encapsulate them into class objects. The swagger client also provides documentation about the API and the data being received that will help during development. Interactions with this swagger client library will be done inside a class called Client and return the response back to the Flask application. Once the data is received from our `Client` class, our application must also process this data further in order to output the data meaningfully to the user. This  includes organising  departures for a stop by platform and time to arrive - by using python's operator module, calculating trip fares based on concession type as entered by user, coordinate information for each stop, current status information and calculating time to arrive or trip duration. By using python iterator and generator functions we can create class/ model objects to encapsulate our data once they are extracted/calculated and yield them to the view. Class objects include: 

`DepartureInformation`: stores route information, times, platform, destination, stop coordinates.

`TripJourney`: stores info for a journey including transport legs / number of transport types used, time to arrive, duration, coordinates.

The application must also handle the parsing/formatting of dates by using python's datetime module and the datutils for timezone conversion from UTC to AEST. This is needed to calculate accurate arrival from the current time. Once the data is passed to the view, iterating through the generator/list using Jinja's templating syntax is needed in order to format the data in a readable format, such as lists to render departure info and journey information. The view will also be responsible for mapping coordinates to google maps using JavaScript and creating forms for users using inputs and select boxes created from the results received from the API to help with trip planning. Users also expect to POST to the flask server, saving their favourite trips for them to view anytime on the dashboard at the index page.



### Routes Overview

`/stops` [GET] ~ ARGS[stop name, date, time, transport type, suburb]

returns stops matching the paramaters entered with links to their departure info, status and map image.

`/stops/departures/<id>` [GET] ARGS[date, time]

returns departures for each platform on the  selected date time

`/stops/status/<id> [GET]`

returns the most current statuses affecting stop

`/trip/planner [GET] ARGS[origin, destination]`

returns a form for the user to select their stops from a select box from the entered stop names in origin and destination

`/trip/journeys [GET] ARGS[page, origin, destination, date, time, concession_type]`

from the form, return all journeys available for the origin point to the destination from the given date and time. calculates duration and total fare of trip based on concession_type selected

`/trip/save` [POST] ARGS[origin, destination]

saves trip information to be retrieved again in the user dashboard



`/` [GET] 

returns saved trips available to the user

###  Dependencies / Modules

- Flask, Jinja chosen as our web framework and templating engine
- Auto-generated swagger client, generated using the swagger codegen java applet
- datetime / dateutils for formatting or parsing  datetime objects or strings
- Python's standard library module operator for sorting lists of class / dict objects by attributes or keys
- JSON for caching and saving favourite trips



### Project File Structure



```
├── client_class.py # Class Module to interact with swagger
├── config
│   └── default.py # server config, including API Key
├── __init__.py
├── models
│   ├── departure_info.py # Model to store our departure information
│   └── trip_journey.py # Model to store our trip journey data
├── server.py
├── services
│   ├── app_locals.py # constants
│   ├── cache_class.py # caching service
│   ├── data_service.py # module to handle algorithm
│   └── swagger_instance.py # swagger instance configuration dependency
└── templates # Jinja templates
    ├── departures.jinja2
    ├── index.jinja2
    ├── journeys.jinja2
    ├── layout.jinja2
    ├── stops.jinja2
    └── trip-planner.jinja2

```

