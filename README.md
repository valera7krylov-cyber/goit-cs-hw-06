# GoIT CS Homework 06

A simple web application built with Python's standard library. It uses
an HTTP server to serve web pages, a UDP socket server to process
submitted messages, and MongoDB to store them.

## Technologies

-   Python 3.12
-   HTTP Server (`http.server`)
-   UDP Sockets (`socket`)
-   Multiprocessing (`multiprocessing`)
-   MongoDB
-   PyMongo
-   Docker
-   Docker Compose

## Project Structure

``` text
goit-cs-hw-06/
├── main.py
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── .dockerignore
├── README.md
├── templates/
│   ├── index.html
│   ├── message.html
│   └── error.html
└── static/
    ├── style.css
    └── logo.png
```

## Features

-   Serves HTML pages using Python's built-in HTTP server.
-   Serves static files, including CSS and images.
-   Handles form submissions through HTTP POST requests.
-   Sends submitted messages to a separate UDP socket server.
-   Runs the UDP server in a separate process.
-   Stores messages in MongoDB.
-   Displays a custom 404 error page for missing resources.
-   Runs the application and MongoDB with Docker Compose.
-   Persists database data in a Docker volume.

## Requirements

-   Docker Desktop
-   Docker Compose

## Run the Application

Clone the repository:

``` bash
git clone https://github.com/valera7krylov-cyber/goit-cs-hw-06.git
cd goit-cs-hw-06
```

Build and start the containers:

``` bash
docker compose up --build
```

Open the application in your browser:

``` text
http://localhost:3000
```

Submit a message using the form on the website. The HTTP server forwards
the submitted data to the UDP server, which stores it in MongoDB.

## Stop the Application

To stop and remove the containers and network:

``` bash
docker compose down
```

MongoDB data is stored in a named Docker volume and remains available
after running this command again.

To remove the containers, network, and the database volume:

``` bash
docker compose down -v
```

**Warning:** The `-v` option deletes the persistent MongoDB volume and
all data stored in it.

## How It Works

1.  A user opens the web application in a browser.
2.  The HTTP server serves the requested HTML page and static files.
3.  The user submits a message through the web form.
4.  The HTTP server receives the POST request and extracts the username
    and message.
5.  The data is encoded as JSON and sent to the UDP socket server.
6.  The UDP server receives the data and creates a MongoDB document.
7.  MongoDB stores the message together with its submission date.

## MongoDB

The application uses:

-   **Database:** `messages_db`
-   **Collection:** `messages`

Each message is stored as a document with the following structure:

``` json
{
    "date": "2026-11-08 15:33:59.928791",
    "username": "example_user",
    "message": "Hello, MongoDB!"
}
```

## Ports

  Service                Port Description
  ------------------- ------- -----------------------------------------------
  HTTP server            3000 Web application
  UDP socket server      5000 Message processing
  MongoDB               27017 Database, available inside the Docker network

## Author

GoIT Python Course --- Computer Systems Homework 06
