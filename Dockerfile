FROM python:3.12-slim


WORKDIR /app


COPY . /app


RUN apt-get update && \
    apt-get install -y apt-utils \
    unixodbc-dev \
    gcc \
    g++ \
    curl \
    gnupg2 \
    lsb-release \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["python", "main.py"]


EXPOSE 5000
