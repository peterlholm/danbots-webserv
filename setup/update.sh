#!/bin/bash

echo update copy to /var/www

cp -r ../* /var/www/webservice

DATE=`date +%x`
echo "INSTALLED=\"$DATE\"\n" >/var/www/webservice/webservice/installed.py

echo restarting service
systemctl restart webservice.service
