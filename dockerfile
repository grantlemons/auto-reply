ARG USERNAME=discord
FROM alpine:latest

# install python
RUN apk add py3-pip build-base
RUN apk add --update --no-cache python3-dev && ln -sf python3 /usr/bin/python

# configure folder
RUN adduser -D discord
RUN mkdir /home/discord/auto-reply/
COPY ./ /home/discord/auto-reply/
RUN chown -R discord /home/discord/auto-reply/
RUN chmod -R 711 /home/discord/auto-reply/

USER discord
RUN pip3 install discord.py python-dotenv --user

WORKDIR /home/discord/auto-reply/
CMD ["python", "/home/discord/auto-reply/main.py"]