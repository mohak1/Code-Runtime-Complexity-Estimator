FROM python:3.10-slim

# copy requirements
COPY requirements.txt ./app/

# install requirements
RUN pip install -r app/requirements.txt

# copy code files
COPY app/. ./app/

# set an env variable to decide compiler URL
ENV is_dockerised=True

# document the port
EXPOSE 8000

# update packages and install curl
RUN apt-get update
RUN apt-get install curl -y

# start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
