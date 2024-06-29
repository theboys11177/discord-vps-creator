# Discord Docker VPS Bot
The official discord bot which creates docker vps(s) on is-a.space

Support Server: https://discord.gg/ctpG8apzC3

Features
- Quick and easy deployment
- SSH (Using tmate. or using serveo.net if editing the script to use `ssh -R $HOSTNAME:22:localhost:22 serveo.net` instead of tmate -F. however tmate has more uptime)
- Uses docker (so you could use this on anything, Even your shitty ahh computer)
- Has creation and removeal and listing of servers
- Supports Debian 12 and Ubuntu 22.04
- A customizeable install script and docker image.
- Uses slash commands
- Start/stop of vps(s)

Work in progress (most likely will never happen without you guys)
- Nodeable support/Shards
- Alpine Linux Support (it exists but never works)
- Systemctl Support
- Spec Limiter

The creation of vps(s)
- Go in any channel
- type /deploy-ubuntu or /deploy-debian (based on what os) and wait as it deploys instant. the bot will dm you with the command to ssh
- Open your cmd and type in the ssh command.

Req:
- Your bot host must be linux and has docker installed, We recommand ubuntu or debian or alpine as the OS.

How to use:
- Download the latest release off the releases 
- Install python3.10 (if you dont have it)
- Go edit the main.py file and look for the TOKEN line and give it your bot token, You get it from [here](<discord.dev>)
- Run the file

Too lazy to host your own bot or want to test it out? Invite ours using this invite link: https://discord.com/oauth2/authorize?client_id=1249856618468737104&permissions=8&integration_type=0&scope=bot
