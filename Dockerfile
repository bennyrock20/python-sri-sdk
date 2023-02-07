FROM fedora:35

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

RUN dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    git \
    && dnf clean all


RUN mkdir /app
WORKDIR /app


# Install Pipenv
RUN pip3 install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /app/

# Install dependencies

RUN pipenv install --dev

# Copy project

COPY . /app/

# Run server

ENTRYPOINT ["pipenv", "run"]




