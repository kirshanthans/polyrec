FROM python:3.7-alpine

COPY . /polyrec
WORKDIR /polyrec

RUN pip install -r requirements.txt

CMD ["sh"]