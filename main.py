from discord import Client
from discord import NotFound as discNotFound
from json import load
from os import getenv
from asyncio import get_event_loop
from asyncio import sleep as asnycsleep
from dotenv import load_dotenv
import logging

# input / output
logging.basicConfig(filename='discord.log', level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf8')

with open('commands.json') as json_file:
    guilds = load(json_file)


# env variables
load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')
OWNER_ID = getenv('BOT_OWNER')
CONTROL_GUILD = getenv('CONTROL_GUILD')


# objects
client = Client()
loop = get_event_loop()
#slash = SlashCommand(client)


# variables
replied_messages = []

# parent - child deletion
@client.event
async def on_message_delete(message):
    for grouped_messages in replied_messages:
        try:
            if message == grouped_messages['parent']:
                await grouped_messages['child'].delete()
            if message == grouped_messages['child']:
                await grouped_messages['parent'].delete()
        except discNotFound:
            pass
    
# what to do on a message
@client.event
async def on_message(message):
    # responding
    for guild in guilds:
        if guilds[guild]['id'] == message.guild.id:
            for command in guilds[guild]['commands']:
                command_output = guilds[guild]['commands'][command]
                command_prefix = guilds[guild]['prefix']
                
                # shutdown and logging
                if message.author.id == int(OWNER_ID):
                    if message.guild.id == int(CONTROL_GUILD):
                        if message.content == f'{command_prefix}stop':
                            try:
                                await message.delete()
                                await asnycsleep(0.2)
                                await client.close()
                                logging.info('Command Triggered Stop')
                                logging.info('Stopping')
                            except:
                                try:
                                    quit()
                                except:
                                    pass
                    else:
                        print( f'{message.author}: {message.content}' )
                        logging.info( f'{message.author}: {message.content}' )
                
                if message.content == f'{command_prefix}{command}':
                    print( f'{command}: {command_output}' )
                    sent_message = await message.reply(f'{command_output}', mention_author=False)
                    replied_messages.append( {'parent': message, 'child': sent_message} )
    
# run it
try:
    loop.run_until_complete(client.start(TOKEN, bot = True))
except KeyboardInterrupt:
    try:
        loop.run_until_complete(client.close())
    except:
        pass
    logging.warn('Keyboard triggered stop')
    logging.info('Stopping')
except:
    loop.run_until_complete(client.close())
    logging.warn('Command line or error triggered stop')
    logging.info('Stopping')
finally:
    loop.close()