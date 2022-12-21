FROM python:3.7-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install -U pip wheel cython \
    && PIP_NO_BINARY=psycopg2 pip install -r requirements.txt

RUN python -m nltk.downloader vader_lexicon
EXPOSE 5000

CMD [ "flask", "run", "-h", "0.0.0.0" ]
