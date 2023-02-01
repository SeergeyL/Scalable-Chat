# pull official base image
FROM python:3.10-bullseye

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

# default port
EXPOSE 8000/tcp

# run uvicorn server
CMD ["uvicorn", "main:app", "--reload", "--workers", "1", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
