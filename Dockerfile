
FROM python:3.10
COPY ./server-side .
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
