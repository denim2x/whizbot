# Whizbot
Engage into interesting conversations with this multi-purpose chatbot

## Description
This project aims to develop an interesting conversational agent with the following capabilities:
 - describes itself, its abilities and others;
 - answers open-ended questions with information from Wikipedia;
 - displays Weather data;
 - shows Chuck Norris jokes.

## Architecture
### Frontend
- HTML5
- JavaScript (ES6)
- CSS3
- Rivets.js
- Domtastic

### Backend
- Web server developed in Python3 with BareASGI, hosted on CloudFoundry service;
- Watson Assistant, for classifying intents and modeling appropriate responses;
- Weather Company Data for IBM Bluemix - for retrieving weather information;
- Wikipedia Search API - for retrieving answers to open-ended questions;
- Chuck Norris jokes API.

