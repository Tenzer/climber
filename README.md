# Climber

A Flask application for handling a fussball ladder tournament system.


## Docker

In order to get started with Docker, you first have to build the image by running the following command inside the project folder:

    docker build --tag climber .

After that you will be able to start a container with the image by running:

    docker run --detach --publish-all --name=climber climber

Then check the port it is available on by using:

    docker port climber 5000
