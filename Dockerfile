# syntax = docker/dockerfile:1.3
FROM python:3.10

WORKDIR /src

COPY ./src /src
# Dataset for demo purposes
COPY src/service/consumers/data/income-biased.csv ./data/income-biased.csv
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /usr/share/man/man1 /usr/share/man/man2

RUN apt-get update && \
apt-get install -y --no-install-recommends \
        openjdk-11-jre


#RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000"]
