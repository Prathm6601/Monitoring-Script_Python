# Monitoring-Script_Python

Install all Python dependency

First, install the Python then run the below command
- #pip install Flask [Flask is a micro web framework for Python used for building web applications]
- #pip install Flask-BasicAuth [ Flask-BasicAuth is an extension for adding HTTP basic access authentication to Flask routes.]
- #pip install psycopg2 [psycopg2 is a PostgreSQL adapter for Python. It's used for connecting Flask applications to PostgreSQL databases.]
- #pip install docker [docker is a Python library for interacting with the Docker Engine API. It's used for monitoring Docker containers in your Flask application]
- #pip install humanize [humanize is a Python package for making numbers more readable by adding commas and converting large numbers to human-readable formats]

- #python3 pythonscriptname.py [run this command]
  
If you want to run this process continuously on a background run the below command
- #nohup sudo python3 prathmcom2.py &
  
If you want to stop this process run the below command
- #ps aux | grep pythonscriptname.py
  
Then kill all the running process
- #kill PID

To run the email notification script 
- #sudo nohup sudo python3 apr24mail.py &
