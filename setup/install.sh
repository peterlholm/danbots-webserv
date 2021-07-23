#!/bin/bash

echo copy to /var/www

mkdir /var/www/webservice

cp -r ../* /var/www/webservice

echo setup apache conf

ln -s /var/www/webservice/apache/webservice.conf /etc/apache2/sites-available


sudo apt install libapache2-mod-wsgi-py3

sudo apt install pigpiod
systemctl enable pigpiod.service
systemctl restart pigpiod.service

pip3 install -r ../requirements.txt

#a2ensite webservice
#systemctl restart apache2

# as system service

cp ../apache/webservice.service /etc/systemd/system/

systemctl start pigpiod.service

systemctl enable webservice.service
systemctl restart webservice.service
