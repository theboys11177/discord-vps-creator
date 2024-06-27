# Setup for packages:
# pip install docker discord


import discord
from discord.ext import commands, tasks
import docker
import time
import re
import os
import concurrent.futures

TOKEN = '' # input the stupid token here.

intents = discord.Intents.all()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

client = docker.from_env()

SERVER_LIMIT = 12
database_file = 'database.txt'

executor = concurrent.futures.ThreadPoolExecutor(max_workers=150)

def add_to_database(user, container_name, ssh_command):
    with open(database_file, 'a') as f:
        f.write(f"{user}|{container_name}|{ssh_command}\n")

def remove_from_database(ssh_command):
    if not os.path.exists(database_file):
        return
    with open(database_file, 'r') as f:
        lines = f.readlines()
    with open(database_file, 'w') as f:
        for line in lines:
            if ssh_command not in line:
                f.write(line)

def get_user_servers(user):
    if not os.path.exists(database_file):
        return []
    servers = []
    with open(database_file, 'r') as f:
        for line in f:
            if line.startswith(user):
                servers.append(line.strip())
    return servers

def count_user_servers(user):
    return len(get_user_servers(user))

@bot.event
async def on_ready():
    change_status.start()
    print(f'Bot is ready. Logged in as {bot.user}')
    await bot.tree.sync()

@tasks.loop(minutes=1)
async def change_status():
    await bot.change_presence(activity=discord.Game(name="with VPS(s)"))

@bot.tree.command(name="list", description="Lists all your servers")
async def list_servers(interaction: discord.Interaction):
    user = str(interaction.user)
    servers = get_user_servers(user)
    if servers:
        embed = discord.Embed(title="Your Servers", color=0x00ff00)
        for server in servers:
            _, container_name, _ = server.split('|')
            embed.add_field(name=container_name, value="Type: Dedicated Docker Conatainer ", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(embed=discord.Embed(description="You have no servers.", color=0xff0000))

@bot.tree.command(name="help", description="Shows the help message")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", color=0x00ff00)
    embed.add_field(name="/deploy-ubuntu", value="Creates a new server with Ubuntu 22.04", inline=False)
    embed.add_field(name="/deploy-debian", value="Creates a new server with Debian 12", inline=False)
    embed.add_field(name="/deploy-alpine", value="Creates a new server with Alpine", inline=False)
    embed.add_field(name="/remove <ssh_command/Name>", value="Removes a server", inline=False)
    embed.add_field(name="/restart <ssh_command/Name>", value="Restart a server (Disabled)", inline=False)
    embed.add_field(name="/start <ssh_command/Name>", value="Start a server (Disabled)", inline=False)
    embed.add_field(name="/stop <ssh_command/Name>", value="Stop a server (Disabled)", inline=False)
    embed.add_field(name="/list", value="List all your server", inline=False)
    embed.add_field(name="/support", value="Provides support server link", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="support", description="Provides support server link")
async def support(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(description="Join our support server: https://discord.gg/is-a-space", color=0x00ff00))

async def get_ssh_session_line(container):
    def get_ssh_session(logs):
        match = re.search(r'ssh session: (ssh [^\n]+)', logs)
        if match and "ro-" not in match.group(1):
            return match.group(1)
        return None

    ssh_session_line = None
    max_attempts = 300000
    attempt = 0

    while attempt < max_attempts:
        logs = container.logs().decode('utf-8')
        ssh_session_line = get_ssh_session(logs)
        if ssh_session_line:
            break
        attempt += 1

    return ssh_session_line

async def create_server_task(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(description="Creating server, This takes a few seconds.\n```running apt update\nrunning apt install tmate -y\nrunning tmate -F```", color=0x00ff00))
    user = str(interaction.user)
    if count_user_servers(user) >= SERVER_LIMIT:
        await interaction.followup.send(embed=discord.Embed(description="Error: Server Limit-reached\n\nLog: ```Failed to run apt update\nFailed to run apt install tmate\nFailed to run tmate -F\nError: Server Limit-reached```", color=0xff0000))
        return

    image = "ubuntu:22.04"
    commands = """
    apt update && \
    apt install -y tmate && \
    tmate -F
    """

    container = client.containers.run(image, command="sh -c '{}'".format(commands), detach=True, tty=True)

    ssh_session_line = await get_ssh_session_line(container)
    if ssh_session_line:
        await interaction.user.send(embed=discord.Embed(description=f"### Successfully created VPS\n SSH Session Command: ```{ssh_session_line}```Powered by [is-a.space](https://discord.gg/is-a-space)\nOS:Ubuntu 22.04", color=0x00ff00))
        add_to_database(user, container.name, ssh_session_line)
        await interaction.followup.send(embed=discord.Embed(description="Server created successfully. Check your DMs for details.", color=0x00ff00))
    else:
        await interaction.followup.send(embed=discord.Embed(description="Something went wrong or the server is taking longer than expected. if this problem continues, Contact Support.", color=0xff0000))
        container.stop()
        container.remove()

async def create_server_task_debian(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(description="Creating server, This takes a few seconds.\n\nLog:```running apt update\nrunning apt install tmate -y\nrunning tmate -F```", color=0x00ff00))
    user = str(interaction.user)
    if count_user_servers(user) >= SERVER_LIMIT:
        await interaction.followup.send(embed=discord.Embed(description="Error: Server Limit-reached\n```Failed to run apt update\nFailed to run apt install tmate\nFailed to run tmate -F\nError: Server Limit-reached```", color=0xff0000))
        return

    image = "debian:12"
    commands = """
    apt update && \
    apt install -y tmate && \
    tmate -F
    """

    container = client.containers.run(image, command="sh -c '{}'".format(commands), detach=True, tty=True)

    ssh_session_line = await get_ssh_session_line(container)
    if ssh_session_line:
        await interaction.user.send(embed=discord.Embed(description=f"### Successfully created VPS\n SSH Session Command: ```{ssh_session_line}```Powered by [is-a.space](https://discord.gg/is-a-space)\nOS: Debian 12", color=0x00ff00))
        add_to_database(user, container.name, ssh_session_line)
        await interaction.followup.send(embed=discord.Embed(description="Server created successfully. Check your DMs for details.", color=0x00ff00))
    else:
        await interaction.followup.send(embed=discord.Embed(description="Something went wrong or the server is taking longer than expected. if this problem continues, Contact Support.", color=0xff0000))
        container.stop()
        container.remove()


async def create_server_task_alpine(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(description="Creating server, This takes a few seconds.\n\n```apk update\napk add --no-cache tmate\necho 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories\napk add --no-cache tmate\ntmate -F```", color=0x00ff00))
    user = str(interaction.user)
    if count_user_servers(user) >= SERVER_LIMIT:
        await interaction.followup.send(embed=discord.Embed(description="Something went wrong\n\n```Failed to run apk update\nFailed to run apk add --no-cache tmate\necho 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories\nFailed to run apk add --no-cache tmate\nFailed to run tmate -F\nError: Server Limit-reached```", color=0xff0000))
        return

    image = "alpine:3.19"
    commands = """
    apk update && \
    apk add --no-cache tmate && \
    echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \
    apk add --no-cache tmate && \
    tmate -F
    """

    container = client.containers.run(image, command="sh -c '{}'".format(commands), detach=True, tty=True)

    ssh_session_line = await get_ssh_session_line(container)
    if ssh_session_line:
        await interaction.user.send(embed=discord.Embed(description=f"### Successfully created VPS\n SSH Session Command: ```{ssh_session_line}```Powered by [is-a.space](https://discord.gg/is-a-space)\nOS: Debian 12", color=0x00ff00))
        add_to_database(user, container.name, ssh_session_line)
        await interaction.followup.send(embed=discord.Embed(description="Server created successfully. Check your DMs for details.", color=0x00ff00))
    else:
        await interaction.followup.send(embed=discord.Embed(description="Something went wrong or the server is taking longer than expected. if this problem continues, Contact Support.", color=0xff0000))
        container.stop()
        container.remove()

async def remove_server_task(interaction: discord.Interaction, ssh_command: str):
    user = str(interaction.user)
    servers = get_user_servers(user)
    if any(ssh_command in server for server in servers):
        container_name = next((server.split('|')[1] for server in servers if ssh_command in server), None)
        if container_name:
            container = client.containers.get(container_name)
            container.stop()
            container.remove()
            remove_from_database(ssh_command)
            await interaction.response.send_message(embed=discord.Embed(description="Server removed successfully.", color=0x00ff00))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Server not found.", color=0xff0000))
    else:
        await interaction.response.send_message(embed=discord.Embed(description="Something went wrong trying to delete this server.", color=0xff0000))

async def start_server_task(interaction: discord.Interaction, ssh_command: str):
    user = str(interaction.user)
    servers = get_user_servers(user)
    if any(ssh_command in server for server in servers):
        container_name = next((server.split('|')[1] for server in servers if ssh_command in server), None)
        if container_name:
            try:
                container = client.containers.get(container_name)

                if container.status == 'running':
                    await interaction.response.send_message(embed=discord.Embed(description="Server is already running. Stopping", color=0x00ff00))
                    container.kill()
                    await interaction.response.send_message(embed=discord.Embed(description="Stopped Server.", color=0x00ff00))
                else:
                    container.start()
                    container.exec_run("tmate -F", detach=True)
                    ssh_session_line = await get_ssh_session_line(container)
                    if ssh_session_line:
                        await interaction.user.send(embed=discord.Embed(description=f"### Successfully started Server\nSSH Session Command: ```{ssh_session_line}```", color=0x00ff00))
                        await interaction.response.send_message(embed=discord.Embed(description="Server started successfully. Check your DMs for details.", color=0x00ff00))
                    else:
                        await interaction.response.send_message(embed=discord.Embed(description="Failed to start server: Unable to get SSH session.", color=0xff0000))
            except docker.errors.APIError as e:
                await interaction.response.send_message(embed=discord.Embed(description=f"Failed to start server: {str(e)}", color=0xff0000))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Server not found.", color=0xff0000))
    else:
        await interaction.response.send_message(embed=discord.Embed(description="Something went wrong trying to start this server.", color=0xff0000))

async def stop_server_task(interaction: discord.Interaction, ssh_command: str):
    user = str(interaction.user)
    servers = get_user_servers(user)
    if any(ssh_command in server for server in servers):
        container_name = next((server.split('|')[1] for server in servers if ssh_command in server), None)
        if container_name:
            try:
                container = client.containers.get(container_name)
                
                if container.status == 'running':
                    container.stop()
                    await interaction.response.send_message(embed=discord.Embed(description="Server stopped successfully.", color=0x00ff00))
                else:
                    await interaction.response.send_message(embed=discord.Embed(description="Server is not running.", color=0xff0000))
            except docker.errors.APIError as e:
                await interaction.response.send_message(embed=discord.Embed(description=f"Failed to stop server: {str(e)}", color=0xff0000))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Server not found.", color=0xff0000))
    else:
        await interaction.response.send_message(embed=discord.Embed(description="Something went wrong trying to stop this server.", color=0xff0000))

async def restart_server_task(interaction: discord.Interaction, ssh_command: str):
    user = str(interaction.user)
    servers = get_user_servers(user)
    if any(ssh_command in server for server in servers):
        container_name = next((server.split('|')[1] for server in servers if ssh_command in server), None)
        if container_name:
            try:
                container = client.containers.get(container_name)
                
                if container.status == 'running':
                    container.restart()
                    container.exec_run("tmate -F", detach=True)
                    ssh_session_line = await get_ssh_session_line(container)
                    if ssh_session_line:
                        await interaction.user.send(embed=discord.Embed(description=f"### Successfully restarted Server\nNew SSH Session Command: ```{ssh_session_line}```", color=0x00ff00))
                        await interaction.response.send_message(embed=discord.Embed(description="Server restarted successfully. Check your DMs for details.", color=0x00ff00))
                    else:
                        await interaction.response.send_message(embed=discord.Embed(description="Failed to restart server: Unable to get SSH session.", color=0xff0000))
                else:
                    await interaction.response.send_message(embed=discord.Embed(description="Failed to restart server: Server is not running.", color=0xff0000))
            except docker.errors.APIError as e:
                await interaction.response.send_message(embed=discord.Embed(description=f"Failed to restart server: {str(e)}", color=0xff0000))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="Server not found.", color=0xff0000))
    else:
        await interaction.response.send_message(embed=discord.Embed(description="Something went wrong trying to restart this server.", color=0xff0000))

@bot.tree.command(name="deploy-ubuntu", description="Creates a new server with Ubuntu 22.04.")
async def deploy(interaction: discord.Interaction):
    await create_server_task(interaction)

@bot.tree.command(name="deploy-debian", description="Creates a new server with Debian 12.")
async def deploy(interaction: discord.Interaction):
    await create_server_task_debian(interaction)

# this is disabled because its broken
# @bot.tree.command(name="deploy-alpine", description="Creates a new server with Alpine linux.")
# async def deploy(interaction: discord.Interaction):
#    await create_server_task_alpine(interaction)

@bot.tree.command(name="remove", description="Removes a server")
async def remove(interaction: discord.Interaction, ssh_command: str):
    await remove_server_task(interaction, ssh_command)

bot.run(TOKEN)
