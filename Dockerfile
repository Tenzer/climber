FROM ubuntu:14.04

# Install PIP for Python 3
RUN apt-get update && apt-get install -y python3-pip

# Include source files
ADD . /src

# Install dependencies
RUN pip3 install -r /src/requirements.txt

# Expose the web-app port
EXPOSE 5000

# Run (has to be JSON)
CMD ["python3", "/src/climber.py"]
