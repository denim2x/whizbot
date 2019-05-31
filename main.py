#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import uvicorn
from _bareasgi import Application
from bareasgi_static import add_static_file_provider

from engine import message

here = os.path.abspath(os.path.dirname(__file__))

app = Application()
app.http_router.add({'POST'}, '/message', message)

add_static_file_provider(app, os.path.join(here, 'static'), index_filename='index.html')

port = int(os.getenv('PORT', '80'))
uvicorn.run(app, host='0.0.0.0', port=port)
