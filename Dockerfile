FROM python:3.10.11

WORKDIR /data
COPY . .
RUN pip install --no-cache-dir -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com/simple ipython
ENV PYTHONUNBUFFERED=1
CMD ["python", "app/main.py","update-user-rate-base-volume"]
