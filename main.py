import discord
from discord.ext import commands, tasks
import os
from random import randint
import requests
from datetime import timedelta, datetime
from collections import defaultdict, deque
import asyncio
import json
import time
from dotenv import load_dotenv

#Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Constants
DATA = "kracocksData.json"
SPAM_LIMIT = 5
SPAM_TIME = 7 #Interval de temps
INITIAL_MUTE_TIME = 600 #En secondes
MUTE_INCREMENT = 300 #En secondes
DECREMENT_INTERVAL = 600
MAX_MUTE_TIME = 3600


bot = commands.Bot(command_prefix="/", intents=intents)

#global variables
available_tags = [
    "big breasts",
    "sole female",
    "sole male",
    "anal",
    "group",
    "stockings",
    "lolicon",
    "nakadashi",
    "blowjob",
    "schoolgirl uniform",
    "glasses",
    "rape",
    "full color",
    "shotacon",
    "yaoi",
    "bondage",
    "multi-work series",
    "mosaic censorship",
    "ahegao",
    "males only",
    "incest",
    "x-ray",
    "double penetration",
    "milf",
    "defloration",
    "paizuri",
    "sex toys",
    "dark skin",
    "twintails",
    "futanari",
    "tankoubon",
    "netorare",
    "ponytail",
    "yuri",
    "ffm threesome",
    "femdom",
    "hairy",
    "swimsuit",
    "collar",
    "impregnation",
    "dilf",
    "full censorship",
    "anal intercourse",
    "big penis",
    "kemonomimi",
    "sister",
    "bbm",
    "pantyhose",
    "cheating",
    "sweating",
    "muscle",
    "mind break",
    "masturbation",
    "tentacles",
    "lactation",
    "crossdressing",
    "mmf threesome",
    "big ass",
    "schoolboy uniform",
    "bikini",
    "tomgirl",
    "gloves",
    "mind control",
    "urination",
    "uncensored",
    "kissing",
    "exhibitionism",
    "teacher",
    "pregnant",
    "maid",
    "unusual pupils",
    "females only",
    "handjob",
    "beauty mark",
    "harem",
    "story arc",
    "fingering",
    "mother",
    "lingerie",
    "gender change",
    "huge breasts",
    "footjob",
    "furry",
    "condom",
    "anthology",
    "extraneous ads",
    "cunnilingus",
    "drugs",
    "catgirl",
    "gag",
    "garter belt",
    "horns",
    "piercing",
    "prostitution",
    "small breasts",
    "very long hair",
    "tail",
    "stomach deformation",
    "filming",
    "demon girl",
    "rimjob",
    "blindfold",
    "blackmail",
    "bunny girl",
    "scat",
    "virginity",
    "inflation",
    "bukkake",
    "elf",
    "kimono",
    "bbw",
    "big areolae",
    "tanlines",
    "sole dickgirl",
    "bald",
    "sleeping",
    "bloomers",
    "deepthroat",
    "monster",
    "gyaru"
]
symboles_chimiques_2_lettres = [
    "He", "Li", "Be", "Ne", "Na", "Mg", "Al", "Si", "Cl", "Ar", "Ca", "Sc",
    "Ti", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se",
    "Br", "Kr", "Rb", "Sr", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag",
    "Cd", "In", "Sn", "Sb", "Te", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf",
    "Ta", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At",
    "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "Np", "Pu", "Am", "Cm", "Bk", "Cf",
    "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
]
symboles_chimiques_1_lettres = [
    "H", "B", "C", "N", "O", "F", "P", "S", "K", "V", "Y", "I", "W", "U"
]
message_logs = defaultdict(lambda: deque(maxlen=SPAM_LIMIT))
mute_times = defaultdict(int)
last_spam_time = defaultdict(int)
mute_bypasser = [1173254160137859163] #ID utilisateur
muted = []


def load_data():
    with open(DATA,"r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA, "w") as f:
        json.dump(data, f, indent=4)

loaded_data = load_data()


#Function
def top_most_used_words(words:dict):
    words_as_list = list(words.items())
    res = sorted(words_as_list, key=lambda x:x[1], reverse=True)
    return res


def random_with_N_digits(n):
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


async def mute_user(user):
    if any(role.id in mute_bypasser for role in user.roles):
        print(f"L'utilisateur {user.name} ne sera pas mute")
        return
        
    guild = user.guild
    role = discord.utils.get(guild.roles, name="Muted")

    if not role:
        role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(role, speak=False, send_messages=False, add_reactions=False)

    # Calculer la durée du mute
    current_mute_time = INITIAL_MUTE_TIME + (mute_times[user.id] * MUTE_INCREMENT)
    current_mute_time = min(current_mute_time, MAX_MUTE_TIME)  # Ne pas dépasser la durée maximale
    mute_times[user.id] += 1

    await user.add_roles(role)
    muted.append(user)
    await user.send(f"Vous avez été muté pour {current_mute_time // 60} minutes en raison de spam.")
    await asyncio.sleep(current_mute_time)
    await user.remove_roles(role)
    await user.send("Votre mute est terminé. Veuillez éviter de spammer pour éviter un mute plus long.")


#Events
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    try:
        bot.tree.clear_commands(guild=discord.Object(id=1048696509182529538))
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

@bot.event
async def on_disconect():
    if len(muted) == 0:
        return
    for user in muted:
        guild = user.guild
        role = discord.utils.get(guild.roles, name="Muted")
        await user.remove_roles(role)
        await user.send("Votre mute est terminé. Veuillez éviter de spammer pour éviter un mute plus long.")


@bot.event
async def on_message(message):
    content = message.content.upper()
    author_id = message.author.id
    current_time = message.created_at.timestamp()
    

    
    #Symboles chimiques
    ind = 0
    res = ""

    while ind < len(content):
        temp = ""

        if content[ind] in symboles_chimiques_1_lettres:
            temp = content[ind]
            ind += 1

            if ind < len(content) and (temp + content[ind].lower()) in symboles_chimiques_2_lettres:
                temp += content[ind].lower()
                ind += 1

            res += temp

        elif ind + 1 < len(content) and (content[ind] + content[ind + 1].lower()) in symboles_chimiques_2_lettres:
            res += content[ind] + content[ind + 1].lower()
            ind += 2

        elif content[ind] == " ":
            res += " "
            ind += 1

        else:
            break

    if len(res) == len(content) and res.strip() != "" and author_id != bot.user.id:
        await message.channel.send(
            "Ton message peut être écrit en utilisant les symboles du tableau périodique des éléments : "
            + os.linesep + res
        )


    
    

    #Classement des mots
    for word in message.content.split():
        if word not in loaded_data["words"] and not word.startswith("http") and not word.startswith("/") and not word.startswith("<@") and message.author.id != bot.user.id:
            loaded_data["words"][word] = 0
        elif word in loaded_data["words"]:
            loaded_data["words"][word] += 1
        else:
            return
        save_data(loaded_data)

    
    #Enabling commands
    await bot.process_commands(message)


@bot.event
async def on_user_update(before, after):
    if before.avatar != after.avatar:
        if str(after.id) not in loaded_data["nb_avatar_change"]:
            loaded_data["nb_avatar_change"][str(after.id)] = 0
        loaded_data["nb_avatar_change"][str(after.id)] += 1
        save_data(loaded_data)  # Sauvegarder l'ensemble des données, pas seulement une partie
        print(f"L'utilisateur {after.name} a changé son avatar {loaded_data['nb_avatar_change'][str(after.id)]} fois.")


#Commands
@bot.tree.command(name="bonjour", description="Dit bonjour !")
async def bonjour(interaction: discord.Interaction):
    await interaction.response.send_message(f"Salut, {interaction.user} !")


@bot.tree.command(name="sauce", description="Génère une sauce aléatoire")
async def sauce(interaction: discord.Interaction, args:str = None):
    if interaction.channel_id in [1082046308153577513, 1157620429247238194]:
        global available_tags
        searching = True
        while searching:
            numbers = random_with_N_digits(6)
            url = f"https://nhentai.net/g/{numbers}"
            try:
                r = requests.get(url)
                r.raise_for_status()
                searching = False
                if args is not None:
                    print(args)
                    if args in available_tags:
                        channel_temp = bot.get_channel(1275444262883819590)
                        await channel_temp.send(url)
                        await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=2))
                        message = await channel_temp.fetch_message(channel_temp.last_message_id)
                        if "https://nhentai.net/g/" in message.content and message.embeds:
                            await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=2))
                            embed = message.embeds[0]
                            description = embed.description
                            print(description)
                            if description is None:
                                print("description is None")
                                searching = True
                            elif args not in description:
                                print("args not in description")
                                searching = True
                            else:
                                await interaction.response.send_message(url)

                    else:
                        await interaction.response.send_message("Tag non reconnu. /tags pour voir les tags disponibles")

                else:
                    await interaction.response.send_message(url)
            except requests.exceptions.HTTPError:
                continue

    else:
        await interaction.response.send_message("Je n'ai pas le droit de faire ça ici")


@bot.tree.command(name="shutdown", description="Eteint le bot")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:  # Vérifie si l'utilisateur est admin
        await interaction.response.send_message("Le bot s'éteint...", ephemeral=True)
        await bot.close()  # Éteint le bot
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'éteindre le bot.", ephemeral=True)


@bot.tree.command(name="tags", description="Donne les tags que l'on peut donner en argument avec la commande /sauce")
async def tags(interaction: discord.Interaction):
    if interaction.channel_id in [1082046308153577513, 1157620429247238194]:
        global available_tags
        res = "Voici les tags que je connais : " + os.linesep
        for tag in available_tags:
            res += f"{tag}, "
        await interaction.response.send_message(res)


@bot.tree.command(name="avatar_changes", description="Affiche le nombre de fois qu'un utilisateur à changé d'avatar")
async def avatar_changes(interaction: discord.Interaction, user: discord.Member):
    if interaction.channel_id in [1157620429247238194,1173357208961032262]:
        count = loaded_data["nb_avatar_change"].get(str(user.id), 0)
        await interaction.response.send_message(f"{user.name} a changé son avatar {count} fois.")
    else:
        await interaction.response.send_message("Veuillez utiliser les commandes dans le salon dédié", ephemeral=True)


@bot.tree.command(name="most_used_words", description="Affiche les mots les plus utilisés sur le serveur")
async def most_used_words(interaction: discord.Interaction):
    if interaction.channel_id in [1157620429247238194,1173357208961032262]:
        words = loaded_data["words"]
        place = 1
        res = "Voici le top 10 des mots les plus utilisés : " + os.linesep
        res += "Place. Mot : nombre d'utilisation" + os.linesep
        ordered_words = top_most_used_words(words)
        while place <= 10:
            try:
                word = ordered_words[place-1][0]
                count = ordered_words[place-1][1]
                res += f"{place}. {word} : {count}" + os.linesep
                place += 1
            except:
                break
        await interaction.response.send_message(res)
    else:
        await interaction.response.send_message("Veuillez utiliser les commandes dans le salon dédié", ephemeral=True)




load_dotenv()
TOKEN = os.getenv('TOKEN')

bot.run(TOKEN)