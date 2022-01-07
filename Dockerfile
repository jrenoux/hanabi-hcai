#Pull base image
FROM python:3.8

WORKDIR /hanabi-hcai

#Install  git & curl
#RUN apt-get update -y && apt-get install git curl -y


#Establish a non-root user for runtime
RUN useradd -m hanabi
USER hanabi

#Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/home/hanabi/.local/bin:${PATH}"

#Copy the current dir
COPY . ./

#Install the project
RUN poetry run pip install -U pip && poetry run pip install setuptools==57.5.0 && poetry install --no-interaction --no-ansi

#Expose justpy port
EXPOSE 8062

#RUN the project
CMD ["./start.sh"]
