FROM python:3.7-alpine

RUN mkdir -p /polyrec
WORKDIR /polyrec
RUN pip install pycparser astunparse 

CMD ["sh"]