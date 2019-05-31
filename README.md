# Whizbot
Engage into interesting conversations with this multi-purpose chatbot

## Description
This project interesting conversational agent, beginning with:
 - describing itself and its current abilities;
 - answering open-ended questions with information from Wikipedia;
 - showing Weather data, optionally specifying *location*; if none is given, the user is asked for the desired *city*;
 - telling Chuck Norris jokes, optionally specifying the category; the list of categories can also be requested.

## Implementation
### Frontend
 - languages: HTML5, JavaScript (ES6), CSS3;
 - [Rivets.js](http://rivetsjs.com) - for data-binding;
 - [DOMtastic](https://domtastic.js.org) - for DOM manipulation (and traversal).

### Backend
Python3 ASGI Web server hosted on the [CloudFoundry](https://www.cloudfoundry.org) service.
 - [Uvicorn](http://uvicorn.org/);
 - [BareASGI](https://bareasgi.readthedocs.io/en/latest/) - for serving static files and handling HTTP requests;
 - [Watson Assistant](https://www.ibm.com/cloud/watson-assistant/), for classifying natural language intents ;
 - [Wikipedia Search API](https://www.mediawiki.org/wiki/API:Search) - for retrieving answers to open-ended questions;
 - [Weather Company Data for IBM Bluemix](https://cloud.ibm.com/docs/services/Weather) - for fetching weather information;
 - [Chuck Norris jokes API](https://api.chucknorris.io).

## Details
### Watson Assistant
This project is utilizing two *Assistant* instances:
 - *chatbot* - for regular intent processing;
 - *wikibot* - for storing *search snippets* obtained from *Wikipedia* as *intents* (*questions*) with corresponding *dialog nodes* (*answers*).

The current model supports the following types of inquiries:
 - chatbot-related: *identity, description, capabilities*;
 - weather-related: *general information, temperature, wind speed*, optionally specifying location; uses last-specified location if none is given;
 - Chuck Norris jokes;

In the case where no specific intent is recognized, the query is interpreted as an open-ended question and handled via Wikipedia's Search API; the result is stored in *wikibot* for later retrieval.

## [Business Model Canvas](https://github.com/denim2x/whizbot/releases/tag/0.0.1)
