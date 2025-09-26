FROM python:3.10.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /data
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt ipython

COPY . .

CMD ["python", "app/main.py","update-user-rate-base-volume"]
