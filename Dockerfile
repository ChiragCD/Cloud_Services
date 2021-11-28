FROM python:3.7

ADD random_gen_worker.py .
ADD objects.py .

CMD ["python", "./random_gen_worker.py"]

