FROM ubuntu:latest
WORKDIR /app

# From Lecture 13 slides

RUN apt-get update\
    && apt-get install --no-install-recommends --yes \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    && pip install --upgrade pip\
    && apt-get install -y libmariadbclient-dev-compat libmariadb-dev --yes \
    && apt-get install mariadb-client --yes \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY *.py .
# * just means anything goes there. Learned that working with netCDF files for Sam Shen
RUN pip3 install --compile --no-cache-dir -r requirements.txt

# Run app
