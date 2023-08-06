FROM python:3.11.4-slim-bullseye

WORKDIR /app

COPY . .
RUN pip install .[dev] && pytest -vv

CMD tail -f