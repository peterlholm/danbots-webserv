#!/bin/bash

echo update copy to /var/www

cp -r ../* /var/www/webservice

systemctl restart webservice.service
