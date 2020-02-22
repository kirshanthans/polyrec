FROM python:3.7-alpine

RUN pip install -r requirements.txt

COPY . /polyrec
WORKDIR /polyrec

CMD ["python3", "-m", "examples.demo"]