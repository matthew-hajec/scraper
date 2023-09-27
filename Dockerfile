FROM python:3.11

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Switch to a non-root user
ARG DOCKER_USER=default_user
RUN useradd --create-home $DOCKER_USER
WORKDIR /home/$DOCKER_USER
USER $DOCKER_USER


# Import code
COPY src src

CMD ["python", "src/main.py"]

