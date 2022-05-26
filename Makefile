#
# makfile for installing the danwand webservice
#


help:
	@echo "make install for complete installation"
	@echo "make requirements for python environment"
	@echo "make website for website update"



requirements:
	pip install -r requirements.txt

apache-sw:
	sudo apt install libapache2-mod-wsgi-py3

website:
	@echo copy to /var/www
	-mkdir -p /var/www/webservice
	cp -r apache webservice /var/www/webservice

apacheconf:	/var/www/webservice/apache/webservice.conf
	@echo setup apache conf
	ln -s /var/www/webservice/apache/webservice.conf /etc/apache2/sites-available

# io service
pigpiod:
	sudo apt -y install pigpiod
	systemctl enable pigpiod.service
	systemctl restart pigpiod.service

# access to own PWM module
danwand-user:
	usermod -aG i2c danwand

#a2ensite webservice
#systemctl restart apache2

# as system service
webservice-daemon:
	cp apache/webservice.service /etc/systemd/system/
	systemctl enable webservice.service
	systemctl restart webservice.service

apache-site:	apache-sw apacheconf
	@echo "Installing appache prod site"



install:	requirements webservice-daemon danwand-user pigpiod website