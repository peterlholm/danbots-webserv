#!/bin/bash

echo copy to /var/www

cp -r ../* /var/www/webservice

echo setup apache conf

ln -s /var/www/webservice/apache/webservice.conf /etc/apache2/sites-available

a2ensite webservice
systemctl apache2 restart

