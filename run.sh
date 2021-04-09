#!/bin/bash

. env/bin/activate

export FLASK_APP=webservice
export FLASK_ENV=development

flask run --host 0.0.0.0 --port 5000
