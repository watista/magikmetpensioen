[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)

# Mag ik met pensioen?
A Python Django web based program to check when you can retire. Suitable for dutch users since the retirement age is based on dutch law.

## Getting started
Create a `.env` file in the project root and add the following variables.
|ENV var|Explain|
|-------|-------|
|DEBUG|Django env setting|
|SECRET_KEY|The secret key for Django to use for signing, hashing and signing|
|ALLOWED_HOSTS|The host names that are allowed for the app|
|LOG_LEVEL|The log level, allowed values are: DEBUG, INFO, WARNING, ERROR, or CRITICAL|


## Setup the environment
Create the python environment and install required packages, in these examples the project root is expected to be `/var/www/`, change where necessary.
```
cd /var/www/magikmetpensioen/
python3.10 -m venv env
source env/bin/activate
pip install -r requirements.txt
deactivate
```

## Setup Django
Run the following commands to initialize Django.
```
/var/www/magikmetpensioen/env/bin/python3 manage.py makemigrations
/var/www/magikmetpensioen/env/bin/python3 manage.py migrate
/var/www/magikmetpensioen/env/bin/python3 manage.py collectstatic
```

## Run locally
```
# Run the program
/var/www/magikmetpensioen/env/bin/python3 /var/www/magikmetpensioen/manage.py runserver
# or
source /var/www/magikmetpensioen/env/bin/activate
python3 /var/www/magikmetpensioen/manage.py runserver
```

## Run as systemd with Nginx reverse proxy
Copy the service file and enable the service.
```
cp /var/www/magikmetpensioen/assets/magikmetpensioen.service /etc/systemd/system/magikmetpensioen.service
sudo systemctl daemon-reload
sudo systemctl start magikmetpensioen
sudo systemctl enable magikmetpensioen
```

Copy the Nginx config and start the proxy.
```
cp /var/www/magikmetpensioen/assets/magikmetpensioen.conf /etc/nginx/sites-available/magikmetpensioen.conf
sudo ln -s /etc/nginx/sites-available/magikmetpensioen.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```
