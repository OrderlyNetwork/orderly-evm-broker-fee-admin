FROM python:3.9.6

WORKDIR /data
COPY . .
RUN pip install --no-cache-dir -r requirements.txt ipython
ENV PYTHONUNBUFFERED=1
CMD ["python", "app/main.py","update-user-rate"]
