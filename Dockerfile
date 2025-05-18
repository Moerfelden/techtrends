FROM python:3.8

# copy files from the host to the container filesystem
COPY techtrends/ /techtrends

# define the working directory within the container
WORKDIR /techtrends

RUN pip install -r requirements.txt && python init_db.py

EXPOSE 3111

# commands that should be executed when a Docker container is started from the Docker image
# "--host=0.0.0.0": This argument tells the Flask server to listen on all available IP addresses (0.0.0.0) rather than just localhost (127.0.0.1).
# This is important for allowing external access to the application running inside the container.
CMD ["python", "app.py", "--host=0.0.0.0"]
