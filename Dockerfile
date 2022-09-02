FROM python:3

# RUN git clone https://github.com/iamobiwan/endurance-vpn-bot.git
WORKDIR /endurance-vpn-bot
COPY . .
VOLUME [ "/endurance-vpn-bot/logs" ]
RUN pip install -r requirements.txt

CMD [ "python", "endurance.py" ]
# CMD [ "/bin/bash" ]