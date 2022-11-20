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
EXPOSE 80

# start the server
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]