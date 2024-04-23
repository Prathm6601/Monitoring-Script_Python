from flask import Flask, render_template, request
from threading import Thread
import subprocess
import psycopg2
import docker
import humanize
from flask_basicauth import BasicAuth

app = Flask(__name__)
basic_auth = BasicAuth(app)

# Configure basic authentication
app.config['BASIC_AUTH_USERNAME'] = 'nira'
app.config['BASIC_AUTH_PASSWORD'] = 'Nira@123'
app.config['BASIC_AUTH_FORCE'] = True

# Global variables to store PM2 logs
pm2_dev_logs = ""
pm2_qa_logs = ""
pm2_uat_logs = ""

# Function to connect to PostgreSQL
def connect_to_postgresql(host, database, user, password):
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

# Function to execute query on PostgreSQL
def execute_query(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

# Function to monitor Docker containers
def monitor_containers():
    client = docker.from_env()
    containers = client.containers.list()
    running_count = 0
    stopped_count = 0
    paused_count = 0
    container_info = []

    for container in containers:
        if container.status == 'running':
            running_count += 1
        elif container.status == 'exited':
            stopped_count += 1
        elif container.status == 'paused':
            paused_count += 1

        stats = container.stats(stream=False)
        cpu_usage = "{:.2f}".format((stats['cpu_stats']['cpu_usage']['total_usage'] / stats['cpu_stats']['system_cpu_usage']) * 100)
        memory_usage = humanize.naturalsize(stats['memory_stats']['usage'])

        info = {
            "ID": container.short_id,
            "Name": container.name,
            "Status": container.status,
            "CPU Usage": cpu_usage + " %",
            "Memory Usage": memory_usage,
        }
        container_info.append(info)

    return running_count, stopped_count, paused_count, container_info

# Function to retrieve PM2 logs and limit to the latest 100 logs for Dev environment
def retrieve_pm2_dev_logs():
    global pm2_dev_logs
    pm2_dev_logs = ""  # Initialize pm2_dev_logs as an empty string
    # Execute pm2 logs Nira_dev command and limit to the latest 100 logs
    process = subprocess.Popen(['sudo', 'pm2', 'logs', 'Nira_dev', '--lines', '100'], stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        pm2_dev_logs += line.decode('utf-8')
    process.stdout.close()
    # Split the logs into lines and keep only the latest 100 lines
    pm2_dev_logs = '\n'.join(pm2_dev_logs.split('\n')[-100:])

# Function to retrieve PM2 logs and limit to the latest 100 logs for QA environment
def retrieve_pm2_qa_logs():
    global pm2_qa_logs
    pm2_qa_logs = ""  # Initialize pm2_qa_logs as an empty string
    # Execute pm2 logs Nira_qa command and limit to the latest 100 logs
    process = subprocess.Popen(['sudo', 'pm2', 'logs', 'Nira_qa', '--lines', '100'], stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        pm2_qa_logs += line.decode('utf-8')
    process.stdout.close()
    # Split the logs into lines and keep only the latest 100 lines
    pm2_qa_logs = '\n'.join(pm2_qa_logs.split('\n')[-100:])

# Function to retrieve PM2 logs and limit to the latest 100 logs for UAT environment
def retrieve_pm2_uat_logs():
    global pm2_uat_logs
    pm2_uat_logs = ""  # Initialize pm2_uat_logs as an empty string
    # Execute pm2 logs Nira_uat command and limit to the latest 100 logs
    process = subprocess.Popen(['sudo', 'pm2', 'logs', 'Nira_uat', '--lines', '100'], stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        pm2_uat_logs += line.decode('utf-8')
    process.stdout.close()
    # Split the logs into lines and keep only the latest 100 lines
    pm2_uat_logs = '\n'.join(pm2_uat_logs.split('\n')[-100:])

# Route to display the main page with buttons for Docker, Database, and PM2 logs
@app.route('/')
def main_page():
    return render_template('main.html')

# Route to handle the Docker logs request
@app.route('/docker_logs')
def docker_logs():
    # Monitor Docker containers and fetch logs
    running_count, stopped_count, paused_count, containers = monitor_containers()
    return render_template('docker_logs.html', running_count=running_count, stopped_count=stopped_count, paused_count=paused_count, containers=containers)

# Route to handle the Database logs request
@app.route('/database_logs')
def database_logs():
    # PostgreSQL connection details
    host = "192.168.1.23"
    user = "admin"
    password = "Admin@2024"

    # List of databases to collect logs from
    databases = ["hrms_dev", "hrms_qa", "hrms_uat"]  # Add your database names here

    # Query to collect logs
    query = "SELECT client_addr, datname, usename, application_name, query_start, query FROM pg_stat_activity;"

    logs_data = []  # Store logs data from all databases

    for db in databases:
        # Connect to PostgreSQL for each database
        conn = connect_to_postgresql(host, db, user, password)
        if conn:
            # Execute query for the database
            rows = execute_query(conn, query)
            if rows:
                logs_data.extend(rows)
            conn.close()

    return render_template('database_logs.html', logs=logs_data)

# Route to handle the PM2 logs request for Dev environment
@app.route('/pm2_dev_logs')
def pm2_dev_logs():
    global pm2_dev_logs
    if not pm2_dev_logs:
        retrieve_pm2_dev_logs()  # Retrieve PM2 logs if not already fetched
        return render_template('loading.html')  # Display loading message while fetching logs
    else:
        return render_template('pm2_dev_logs.html', pm2_dev_logs=pm2_dev_logs)

# Route to handle the PM2 logs request for QA environment
@app.route('/pm2_qa_logs')
def pm2_qa_logs():
    global pm2_qa_logs
    if not pm2_qa_logs:
        retrieve_pm2_qa_logs()  # Retrieve PM2 logs if not already fetched
        return render_template('loading.html')  # Display loading message while fetching logs
    else:
        return render_template('pm2_qa_logs.html', pm2_qa_logs=pm2_qa_logs)

# Route to handle the PM2 logs request for UAT environment
@app.route('/pm2_uat_logs')
def pm2_uat_logs():
    global pm2_uat_logs
    if not pm2_uat_logs:
        retrieve_pm2_uat_logs()  # Retrieve PM2 logs if not already fetched
        return render_template('loading.html')  # Display loading message while fetching logs
    else:
        return render_template('pm2_uat_logs.html', pm2_uat_logs=pm2_uat_logs)

if __name__ == "__main__":
    # Start threads to retrieve PM2 logs asynchronously
    pm2_dev_thread = Thread(target=retrieve_pm2_dev_logs)
    pm2_dev_thread.daemon = True
    pm2_dev_thread.start()

    pm2_qa_thread = Thread(target=retrieve_pm2_qa_logs)
    pm2_qa_thread.daemon = True
    pm2_qa_thread.start()

    pm2_uat_thread = Thread(target=retrieve_pm2_uat_logs)
    pm2_uat_thread.daemon = True
    pm2_uat_thread.start()

    # Run Flask app
    app.run(host='0.0.0.0', port=5006, debug=True)
