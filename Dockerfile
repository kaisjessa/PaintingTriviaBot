FROM python:3.10
WORKDIR /bot
COPY temp.txt /bot/
RUN pip install -r temp.txt
COPY . /bot
CMD python main.py
