FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y apt-utils && \
    apt-get install -y unixodbc-dev \
    && apt-get install -y curl gnupg2 lsb-release \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y gcc g++ \
    && pip install pyodbc


RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]

EXPOSE 5000