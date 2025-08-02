import discord
from discord.ext import commands
import gspread
from dotenv import load_dotenv
import os
from oauth2client.service_account import ServiceAccountCredentials
from discord.ui import View, Select, Button
from typing import Literal

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("dhab-price-checker-577277a06251.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Classic Price Bot").worksheet("prices")

def get_prices(realm, region):
    records = sheet.get_all_records()
    prices = {}
    for row in records:
        if row["Realm"].lower() == realm.lower() and row["Region"].upper() == region.upper():
            prices[row["Faction"]] = row["Price"]
    return prices

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=1400517495294525575)
    await bot.tree.sync(guild=guild)
    print(f"Synced slash commands to test server: {guild.id}")
    print(f"Logged in as {bot.user}")

# Embed config
EMBED_COLOR = 0x9136E0
EMBED_THUMBNAIL = "https://cdn.discordapp.com/attachments/968858528343285820/1022583408343384104/dhabava.gif"
GENERIC_DESCRIPTION = (
    "Click a menu and select your server to view prices for both factions.\n\n"
    "Click here to sell: <#1400825204749635684>\n"
    "Click here to view payment options: <#1400825204749635684>"
)

# --------- Pandaria WoW Dropdowns ---------
class PandariaUSDropdown(Select):
    def __init__(self):
        options = [discord.SelectOption(label=s, emoji="🇺🇸") for s in [
            "Benediction", "Grobbulus", "Mankrik", "Whitemane",
            "Faerlina", "Pagle", "Bloodsail Buccaneers", "Atiesh", "Arugal"
        ]]
        super().__init__(placeholder="US Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]
        region = "US"
        results = get_prices(realm, region)
        embed = discord.Embed(title=f"Prices for {realm} (US)", description=GENERIC_DESCRIPTION, color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        for faction in ["Horde", "Alliance"]:
            price = results.get(faction)
            if price:
                embed.add_field(name=f"{faction} {realm}", value=f"{price}$ USD / 1K", inline=False)
        await interaction.response.edit_message(embed=embed, view=PandariaView())

class PandariaEUDropdown(Select):
    def __init__(self):
        options = [discord.SelectOption(label=s, emoji="🇪🇺") for s in [
            "Gehennas", "Firemaw", "Golemagg", "Pyrewood Village",
            "Mirage Raceway", "Everlook", "Venoxis", "Lakeshire",
            "Sulfuron", "Auberdine", "Mandokir"
        ]]
        super().__init__(placeholder="EU Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]
        region = "EU"
        results = get_prices(realm, region)
        embed = discord.Embed(title=f"Prices for {realm} (EU)", description=GENERIC_DESCRIPTION, color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        for faction in ["Horde", "Alliance"]:
            price = results.get(faction)
            if price:
                embed.add_field(name=f"{faction} {realm}", value=f"{price}$ USD / 1K", inline=False)
        await interaction.response.edit_message(embed=embed, view=PandariaView())

# --------- Pandaria View ---------
class PandariaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PandariaUSDropdown())
        self.add_item(PandariaEUDropdown())

# --------- Placeholder Views for Other Games ---------
class RetailView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add Retail dropdown/buttons here

class RunescapeView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add Runescape dropdown/buttons here

class POEView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add POE dropdown/buttons here

class AlbionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add Albion dropdown/buttons here

class ClassicWoWView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add Classic dropdowns here

# --------- Slash Command ---------
@bot.tree.command(name="menu", description="Open the price menu for a specific game")
@discord.app_commands.describe(version="Which menu to show (pandaria, retail, runescape, poe, albion, classic)")
async def menu(interaction: discord.Interaction, version: Literal["pandaria", "retail", "runescape", "poe", "albion", "classic"]):
    version = version.lower()

    embed = discord.Embed(title=f"Price Checker: {version.title()}", description=GENERIC_DESCRIPTION, color=EMBED_COLOR)
    embed.set_thumbnail(url=EMBED_THUMBNAIL)
    embed.set_footer(text="Dhab ®")

    if version == "pandaria":
        await interaction.response.send_message(embed=embed, view=PandariaView(), ephemeral=False)
    elif version == "retail":
        await interaction.response.send_message(embed=embed, view=RetailView(), ephemeral=False)
    elif version == "runescape":
        await interaction.response.send_message(embed=embed, view=RunescapeView(), ephemeral=False)
    elif version == "poe":
        await interaction.response.send_message(embed=embed, view=POEView(), ephemeral=False)
    elif version == "albion":
        await interaction.response.send_message(embed=embed, view=AlbionView(), ephemeral=False)
    elif version == "classic":
        await interaction.response.send_message(embed=embed, view=ClassicWoWView(), ephemeral=False)
    else:
        await interaction.response.send_message("Unknown version. Try: pandaria, retail, runescape, poe, albion, classic", ephemeral=True)

load_dotenv()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))