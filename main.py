from discord import Client
from discord import NotFound as discNotFound
from json import load
from json import dump
from os import getenv
from asyncio import get_event_loop
from asyncio import sleep as asnycsleep
#from dotenv import load_dotenv
import logging

from discord.errors import NotFound

# input / output
logging.basicConfig(filename='discord.log', level=logging.INFO, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logging.warning('------------------------------------------ Starting ------------------------------------------')

with open('commands.json') as json_file:
    guilds = load(json_file)

# env variables
#load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')
OWNER_ID = getenv('BOT_OWNER')
CONTROL_GUILD = getenv('CONTROL_GUILD')


# objects
client = Client()
loop = get_event_loop()


# variables
replied_messages = []

def json_out():
    with open('commands.json', 'w') as outfile:
        dump(guilds, outfile, indent=4)

async def update_commands():
    with open('commands.json', 'w') as outfile:
        dump(guilds, outfile, indent=4)

async def warn(message, warn_message):
    sent_message = await message.reply(f'{warn_message}', mention_author=True)
    replied_messages.append( {'parent': message, 'child': sent_message} )
    logging.info( f'PARENT: {message.id} | {sent_message.id} :CHILD' )
    logging.warning(warn_message)

async def change_settings(content, message):
    # adding responses
    split = content.split(' ')
    if split[0] == '!ADD':
        if len( split ) >= 2:
            if len( split ) >= 3:
                if split[1] == 'GUILD':
                    if not message.guild.name in guilds:
                        guilds[message.guild.name] = {
                            'server_id': message.guild.id,
                            'prefix': split[2],
                            'commands': {}
                        }
                        await warn(message, f'Added guild {message.guild.name} to guilds')
                        await update_commands()
                    else:
                        await warn(message, f'Guild {message.guild.name} already exist in file')
            else:
                await warn(message, 'incorrect argument length')
            if split[1] == f'COMMAND':
                if message.guild.name in guilds:
                    if len( split ) == 4:
                        if not split[2] in guilds[message.guild.name]['commands']:
                            guilds[message.guild.name]['commands'][split[2]] = split[3]
                            await warn(message, f'Added {split[2]} to commands for {message.guild.name}')
                            await update_commands()
                        else:
                            output = guilds[message.guild.name]['commands'][split[2]]
                            await warn(message, f'command already exists with output "{output}"')
                    else:
                        await warn(message, 'incorrect argument length')
                else:
                    await warn(message, f'Guild {message.guild.name} not in guilds')
        else:
            await warn(message, 'incorrect argument length')

    # removing responses
    if split[0] == '!REMOVE':
        if len( split ) >= 2:
            if len( split ) > 1:
                if split[1] == 'GUILD':
                    if message.guild.name in guilds:
                        del guilds[message.guild.name]
                        await warn(message, f'Removed guild {message.guild.name} from guilds')
                        await update_commands()
                    else:
                        await warn(message, f'Guild {message.guild.name} doesn\'t exist in file')
            elif len( split ) < 2:
                await warn(message, 'incorrect argument length')
            if split[1] == 'COMMAND':
                if len( split ) == 3:
                    if split[2] in guilds[message.guild.name]['commands']:
                        del guilds[message.guild.name]['commands'][split[2]]
                        await warn(message, f'Removed {split[2]} from commands for {message.guild.name}')
                        await update_commands()
                else:
                    await warn(message, 'incorrect argument length')
        else:
            await warn(message, 'incorrect argument length')
    
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
    print( f'{message.author}: "{message.content}" DELETED' )
    logging.info( f'{message.author}: "{message.content}" DELETED' )
    
# what to do on a message
@client.event
async def on_message(message):
    # except messages sent by bot
    if message.author != client.user:
        # responding
        multi_commands = message.content.split(';')
        for content in multi_commands:
            content = content.lstrip(' ')
            for guild in guilds:
                if guilds[guild]['server_id'] == message.guild.id:
                    command_prefix = guilds[guild]['prefix']
                    for command in guilds[guild]['commands']:
                        command_output = guilds[guild]['commands'][command]
                        if content == f'{command_prefix}{command}':
                            print( f'{command}: {command_output}' )
                            sent_message = await message.reply(f'{command_output}', mention_author=False)
                            replied_messages.append( {'parent': message, 'child': sent_message} )
                            logging.info( f'PARENT: {message.id} | {sent_message.id} :CHILD' )
                    if content == f'{command_prefix}list':
                        lines = ''
                        for command in guilds[guild]['commands']:
                            output = guilds[guild]['commands'][command]
                            line = f'"{command}" --> "{output}"'
                            lines = (f'{lines}\n{line}')

                        sent_message = await message.channel.send(lines)
                        replied_messages.append( {'parent': message, 'child': sent_message} )
                        logging.info( f'PARENT: {message.id} | {sent_message.id} :CHILD' )
                
                    # shutdown and logging
                    if message.author.id == int(OWNER_ID):
                        if content == f'!shutdown':
                            try:
                                await message.delete()
                                logging.info('Command Triggered Stop')
                                logging.info('Stopping')
                                await asnycsleep(0.2)
                                await client.close()
                            except:
                                json_out()
                                quit()
            
            if message.author.guild_permissions.administrator:
                await change_settings(content, message)
            
                #clearing grouped messages from channel
                if content == '!clear':
                    try:
                        await message.delete()
                    except discNotFound:
                        pass
                    print( len(replied_messages) )
                    for grouped_messages in replied_messages:
                        try:
                            await grouped_messages['parent'].delete()
                            await grouped_messages['child'].delete()
                        except discNotFound:
                            pass
            # logging
            print( f'{message.author}: "{content}"' )
            logging.info( f'{message.author}: "{content}"' )
    
# run it
try:
    loop.run_until_complete(client.start(TOKEN, bot = True))
except KeyboardInterrupt:
    try:
        loop.run_until_complete(client.close())
    except:
        pass
    logging.warning('Keyboard triggered stop')
    logging.info('Stopping')
except:
    loop.run_until_complete(client.close())
    logging.warning('Command line or error triggered stop')
    logging.info('Stopping')
finally:
    loop.close()

json_out()