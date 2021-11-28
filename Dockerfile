FROM python:3.7

ADD random_gen_server.py .

CMD ["python", "./random_gen_server.py"]

