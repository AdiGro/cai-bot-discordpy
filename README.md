# Setup
after opening terminal in project directory:
1. `python -m pip install -r requirements.txt`
2. add your c.ai token and discord bot token in `bot.py` and prefix if required. (by default prefix is `!`)
3. Uncomment the jishaku line if you have jishaku installed and wants to load it for debugging.
4. modify/remove/add c.ai characters in the file models/characters.py. Follow the existing format. You can get avatar urls from your browser's devtools.
5. run the file `bot.py`
6. run `<prefix>sync` in any channel where bot can see your message to sync the commands.

# How to use
The bot runs on the concept of "Rooms". Do not confuse this with the rooms on c.ai.
To chat with a character, user must create a *room* with them. They may also invite other users to the room, or chat alone.
All commands are slash commands and are self-explanatory. You can only have one room at a time.

# Limitations
Currently, we do not store any chat ids in database. So user's chat ids are lost after:
- they disband their room using `/room disband` slash command.
- the bot shuts down.

You can easily export/import rooms data to/from dictionaries. 
