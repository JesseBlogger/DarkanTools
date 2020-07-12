'''
This is the stats module
'''
from datetime import date, datetime
import os
import json
from time import sleep
import requests
from threading import Thread
import subprocess
import os

#TODO: Create a logging system in a logs file(daily like before)
#TODO: Upgrade, debug player commit
#TODO: Create a logs commit->PUSH system <-- You can delay and move to graphing though
#TODO: Document and organize modules.


#VCS/Shell Automation----
def multiple_cmd(*cmds):
    '''
    Runs multiple commands in sub-process shell. Commands are seperated differently depending on OS.
    If it is not windows it will default to a ";" seperator.

    :param cmds: A tuple which is joined/combined into a string with a seperator
    :return: output of shell
    '''
    command = ""
    if "win" in os.sys.platform:
        command = " & ".join(cmds)
    else:
        command = " ; ".join(cmds)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout

def ensure_remote(url, remote_name):
    '''
    Ensures local repo, branch master and remote 'remote_name' exists
    if it does not then we create it and update the cloud to the github version.
    Remember remote 'github' is the name of the local pointer to the actual
    github repository.
    '''

    #----Get current file path
    gitPath = __file__
    # Convert to standard of OS path string
    gitPath = os.path.realpath(gitPath)
    # Just get the folder, then the folder of the folder, go one up
    gitPath = os.path.dirname(gitPath)
    gitPath = os.path.dirname(gitPath)

    #Convert to OS friendly
    gitPath = os.path.realpath(gitPath)
    #----


    if remote_name in str(multiple_cmd(f"cd \"{gitPath}\"", "git remote")):
        print(f"Remote {remote_name} exists, don't worry")
    #If github remote is not in local we need to make it and pull
    else:
        multiple_cmd(f"cd \"{gitPath}\"",
                     "git init .",
                     f"git remote add {remote_name} {url}",
                     f"git pull github master")
        print(f"Created remote {remote_name} and pulled from it!")

def commit_player(username, remote_name) -> str:
    '''
    Commits a folder to remote_name. Remote VCS is
    initialized before in a seperate function.
    players dir is already defined outside scope
    '''
    user_exists, player_info = playerExists(username)
    if username in getRegPlayers():
        return f"{username.title()} already registered..."
    elif user_exists:
        # Add username file to playersdir path
        with open(os.path.join(playersdir, username), mode="w"):
            print(multiple_cmd(f"cd \"{playersdir}\"", "git add .",
                               f"git commit -m \"{date.today()} committed {username} via website\"",
                               f"git push {remote_name} master"))
            return f"Successfully registered {username.title()}!"
    else:
        return "Does not exist in Darkan..."
#VCS/Shell DONE----

#Create a Stat class
class Stat():
    '''
    Stores stats information for future use.
    name of stat
    value is xp
    timestamp is a date the stat was made.

    These are meant to be generated and sent to garbage as they are made
    and left in a dead scope.
    '''

    skill_ID = {"Attack": 0, "Defence": 1, "Strength": 2, "Hitpoints": 3, "Ranged": 4, "Prayer": 5, "Magic": 6,
                "Cooking": 7, "Woodcutting": 8, "Fletching": 9, "Fishing": 10, "Firemaking": 11, "Crafting": 12,
                "Smithing": 13, "Mining": 14, "Herblore": 15, "Agility": 16, "Thieving": 17, "Slayer": 18,
                "Farming": 19, "Runecrafting": 20, "Hunter": 21, "Construction": 22, "Summoning": 23,
                "Dungeoneering": 24}

    def __init__(self, name : str, value : int, timestamp : date):
        self.name = name
        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.name} : {self.value} : {self.timestamp}"

    def getName(self): return self.name
    def getValue(self): return self.value
    def getDate(self): return self.timestamp

#---Player assurance functions
def getPlayerDir():
    '''
    Returns player directory as a string. Compatible with other OS using
    os.path

    :return: String directory path/breadcrumb, dynamic to OS
    '''
    #Magic Python variable
    filePath = __file__

    # Convert to standard of OS path string
    filePath = os.path.realpath(filePath)

    # Just get the folder
    filePath = os.path.dirname(filePath)
    filePath = os.path.realpath(filePath)

    # Now get player directory from this relative path
    playersdir = os.path.join(filePath, "players")

    # Convert to standard of OS
    playersdir = os.path.realpath(playersdir)
    return playersdir

def getRegPlayers():
    '''
    uses the current python file as a path and modifies it
    to find players folder. Players folder is parsed and
    strings are recorded and placed into a list. At the end
    it is gathered and sorted before returning the list.

    :return: a list of strings showing files in "players" folder
    '''
    filePath = __file__

    # Convert to standard of OS path string
    filePath = os.path.realpath(filePath)

    # Just get the folder
    filePath = os.path.dirname(filePath)
    filePath = os.path.realpath(filePath)

    # Now get player directory from this relative path
    playersdir = os.path.join(filePath, "players")

    # Convert to standard of OS
    playersdir = os.path.realpath(playersdir)

    #Sort it before you return the files as a list of strings. Sort returns none btw
    players = os.listdir(playersdir)
    players.sort()

    return players

def playerExists(player) -> tuple:
    '''
    Calls player from API and checks for error by accessing byte information.
    The GET request from HTTPS works even when there is no player. So we check
    after converting the byte file into a string by trying to access a known
    piece of information.

    :return: Tuple type (player existed in API, Actual Stat info)
    '''
    exists = False
    #=====----->The following was created with Postman
    url = "https://darkan.org/api/player/" + player

    payload = {}
    headers= {}

    response = requests.request("GET", url, headers=headers, data = payload)

    #request, below, is the string representation of the player information
    request = response.text.encode('utf8')
    #=====----->

    #Load the API Request as a Python Dictionary
    player_info = json.loads(request)

    #"Stats" is a key. Inside that key is another dictionary of skills. If it does not exist, the GET was a failure
    try:
        player_info = player_info['stats'] #Remove everything else
    except:
        print("Player not found")
        pass
    else:
        print(f"{player} query success")
        exists = True
    return (exists, player_info)
#---Player assurance functions DONE

#---XP tracking assurance
def get_game_stats(player : str) -> dict:
    '''
    Meant for internal use.

    :param player: Insert a Darkan username as a string
    :return: Returns their stats from the Darkan API & adds a username key
    '''
    user_exists, player_info = playerExists(player)

    if user_exists:
        # Now we add meta data to the dict for future reference
        player_info["name"] = player  # Add a name

        #We will add a date meta to it as a string
        player_info["timestamp"] = str(date.today()) #JSON does not accept date objects so its str
        return player_info

def save_stats(stats : dict):
    '''
    Adds a current record of stat changes to a file. with the oldest at the top.
    It finds the appropriate file name to write the stats dictionary via the
    name key, which was added in get_game stats.

    :param stats: Requires dictionary of current statistics
    :return: None
    '''
    #Opens a file in write mode, saving it as PLAYERNAME
    directory = f"{getPlayerDir()}/{stats['name'].lower()}"
    with open(directory, mode="a") as file:
        file.write(str(stats).replace("'", '"') + "\n") #JSON does not accept single quotes

def get_file_stats(player : str, stat_ID : str, days = 90) -> list:
    '''
    stats: list of stats from oldest to newest top to bottom
    newest_dict: Current stat from top to bottom
    current stat: parsed stat_dict
    :return: a list of Stat objects for the specified stat
    '''
    directory = f"players/{player}"
    with open(directory, mode="r") as file:
        stats = []

        #readlines returns a list of lines/string dictionaries of each daily stat report
        for line in file.readlines():
            # Load the file read as a Python Dictionary from the top, starting with the oldest dictionary entry
            newest_stat = json.loads(line)

            #Create the stat for outer scope

            # Total xp is special in that there are not too many nested calls
            if stat_ID == "totalXp":
                #Construct stats, remember it has a date object in constructor
                stamp = datetime.strptime(newest_stat["timestamp"], "%Y-%m-%d").date()
                newest_stat = Stat(stat_ID, newest_stat[stat_ID], stamp)
            # Use the stat_ID keys to signify it is a regular skill
            elif stat_ID.title() in Stat.skill_ID:
                #I need to get all the attributes for the Stat() class but there is a lot of nesting
                #Remember it is name, datetime, xp

                #Name
                stat_name = stat_ID.title()

                #Date
                stamp = datetime.strptime(newest_stat["timestamp"], "%Y-%m-%d").date()

                #XP value, remember the value for skill_ID is its place in the skill dictionary
                skill_index = Stat.skill_ID[stat_name] #Get the index for skills list
                newest_stat = newest_stat["skills"] #Specify into list of stat dictionaries
                newest_stat = newest_stat[skill_index]
                xp_value = newest_stat['xp']

                #Create stat
                newest_stat = Stat(stat_name, xp_value, stamp)
            else:
                print("Wrong stat name")
                break

            #Here we are adding stats to a list with conditions
            if len(stats) is 0:
                # If stats is an empty list add to it
                stats.append(newest_stat)

            elif newest_stat.timestamp <= stats[-1].timestamp or newest_stat is None:
                '''
                newest stat is the newest line of stats, the one below, as a Stat object. Stats[-1] is the previous or
                the one before, making it older. The newest cannot be after so we continue and skip this stat.
                '''
                continue
            else:
                #The stat passed the test and can be added to the list
                stats.append(newest_stat)
        return stats

def gather_game_stats():
    '''
    Gathers all stat information for registered players
    '''
    for player in getRegPlayers():
        stat_record = get_game_stats(player) #Gets stat of the day and puts it in a record
        save_stats(stat_record) #save it into a file and append to it

def clean_stats():
    '''
    Deletes stats recorded on the same day for all players and deletes past 180 days.
    Maybe do this once a month. The delete after 180 days is unwritten.
    '''
    for player in getRegPlayers():
        #Create stats for outer scope, the cleaned_stats is the filtered list of {PLAYERDICT}s
        cleaned_stats = []

        #This will be the most recent {PLAYERDICT} as we iterate
        newest_dict = {}


        with open(f"{getPlayerDir()}/{player}", mode='r') as file:
            #Open the file as a string "{PLAYERDICT} \n" over and over
            player_file = file.readlines()
            player_file

            #Each line is a new {PLAYERDICT}
            for line in player_file:
                # Remember load JSON does not accept single quotes
                line = line.replace("'", '"')

                #Convert to dictionary
                newest_dict = json.loads(line)

                #Always add the first stat dictionary
                if len(cleaned_stats) == 0:
                    cleaned_stats.append(newest_dict)

                #The newest cannot be the oldest. As we parse down the file we get to newer stat_dict, otherwise skip it
                elif newest_dict['timestamp'] <= cleaned_stats[-1]['timestamp']:
                    continue
                else:
                    cleaned_stats.append(newest_dict)

        with open(f"{getPlayerDir()}/{player}", mode='w+') as file:
             for each in cleaned_stats:
                 #Remember load JSON does not accept single quotes, this one may be unnecessary
                 file.write(str(each).replace("'", '"')+"\n")

def sync_stats():
    '''
    Syncronizes stats every 24 hours by calling gather game stats
    then cleaning the data.
    '''
    gather_game_stats()
    clean_stats()
    print("all stats updated & cleaned")

    #60 seconds * 60 minutes * 24 hours
    sleep(60*60*24)
    sync_stats()
#---XP tracking assurance DONE

if __name__ == "__main__":
    #clean_stats()
    #Gathers stats for all registered players
    gather_game_stats()

if __name__ != "__main__":
    #Make sure there is a connection to remote github
    ensure_remote("https://github.com/JesseGuerrero/DarkanTools.git", "github")

    #Update stats everyday if we are out of focus, runs twice on a debug
    Thread(target=sync_stats).start()




