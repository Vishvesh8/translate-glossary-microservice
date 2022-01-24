FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY ./app /app

WORKDIR /app

RUN apt update
RUN apt-get install -y openjdk-11-jre

RUN java --version

RUN pip3 install -r requirements.txt && python3 -m spacy download es_core_news_sm
RUN pip3 install pydantic
