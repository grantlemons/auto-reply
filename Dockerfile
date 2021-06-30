FROM alpine:latest

# install python
RUN apk add py3-pip build-base
RUN apk add --update --no-cache python3-dev && ln -sf python3 /usr/bin/python
RUN pip3 install discord.py python-dotenv

# configure folder
RUN adduser -D discord
RUN mkdir /home/discord/auto-reply/
COPY ./ /home/discord/auto-reply/
RUN chown -R discord /home/discord/auto-reply/
RUN chmod -R 777 /home/discord/auto-reply/
RUN chmod 666 /home/discord/auto-reply/discord.log
RUN chmod 666 /home/discord/auto-reply/commands.json
RUN chmod 555 /home/discord/

USER discord

WORKDIR /home/discord/auto-reply/
#CMD ["python", "/home/discord/auto-reply/main.py"]
ENTRYPOINT [ "python", "/home/discord/auto-reply/main.py" ]