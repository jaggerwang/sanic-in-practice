FROM python:3.7

WORKDIR /app

COPY sources.list /etc/apt/
COPY pip.conf /etc/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-u", "-m", "weiguan.app"]