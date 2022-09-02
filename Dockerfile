FROM python:3

RUN git clone https://github.com/iamobiwan/endurance-vpn-bot.git
WORKDIR /endurance-vpn-bot
RUN pip install -r requirements.txt
RUN python db/migration.py

CMD [ "python", "endurance.py" ]