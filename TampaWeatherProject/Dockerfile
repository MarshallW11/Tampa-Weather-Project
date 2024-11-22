FROM python:3.11

WORKDIR /APP

RUN pip install requests pandas matplotlib datetime
RUN mkdir -p app/output
RUN chmod -R 777 app/output

COPY TampaWeatherProject/main.py /

CMD ["python", "/main.py"]