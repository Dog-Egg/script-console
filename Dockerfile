FROM node:12 as builder

WORKDIR /code

COPY client .

RUN yarn && npm run build

FROM python:3.6

WORKDIR /code

ENV SC_SCRIPTS_DIR="/scripts"
ENV SC_DATA_DIR="/data"

COPY server .
COPY --from=builder /code/build /var/www/html/script-console

RUN pip install -r requirements.txt

VOLUME ["/scripts", "/data"]

EXPOSE 8310

CMD ["python", "server.py", "--host=0.0.0.0"]