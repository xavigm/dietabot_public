FROM python:3.9-alpine

COPY . /usr/src/app/
COPY requirements.txt requirements.txt

# Install system dependencies
RUN apk upgrade && apk add --no-cache \
    bash \
    curl \
    gettext \
    bind-tools \
    grep && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

WORKDIR /usr/src/app/

# Binary directories for Python
ENV PATH="\$PATH:/usr/src/app/bin:/usr/bin:/usr/local/bin:/bin"
# Adding ENV vars

EXPOSE 80
CMD ["python3","-u", "main.py"]


