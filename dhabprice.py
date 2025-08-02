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
retail_sheet = client.open("Classic Price Bot").worksheet("Retail")
currency_sheet = client.open("Classic Price Bot").worksheet("Retail")

def get_prices_multi(region):
    records = currency_sheet.get_all_records()
    prices = []
    for row in records:
        amount = row.get(region)
        currency = row.get("Currency")
        flag = row.get("FLAG EMOJI")
        if amount and currency and flag:
            prices.append(f"{amount} {currency} {flag}")
    return prices

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Channel ID mappings for price checkers
CHANNEL_IDS = {
    "pandaria": 1400892699627749487,
    "retail": 1400892488172048596,
    "classic": 1400543973608653050,
    "poe": 1400520058161074186,
    "runescape": 1400520071155023992,
    "albion": 1400801233471668224,
}

# Embed config
EMBED_COLOR = 0x9136E0
EMBED_THUMBNAIL = "https://cdn.discordapp.com/attachments/968858528343285820/1022583408343384104/dhabava.gif"
GENERIC_DESCRIPTION = (
    "Click a menu and select your server to view prices for both factions.\n\n"
    "Click here to sell: <#1400825204749635684>\n"
    "Click here to view payment options: <#1400825204749635684>"
)

@bot.event
async def on_ready():
    guild = discord.Object(id=1400517495294525575)
    await bot.tree.sync(guild=guild)
    print(f"Synced slash commands to test server: {guild.id}")
    print(f"Logged in as {bot.user}")

    # Send startup embeds to respective channels
    for version, channel_id in CHANNEL_IDS.items():
        view = {
            "pandaria": PandariaView(),
            "retail": RetailView(),
            "classic": ClassicWoWView(),
            "poe": POEView(),
            "runescape": RunescapeView(),
            "albion": AlbionView(),
        }.get(version)
        if view:
            embed = discord.Embed(title=f"Price Checker: {version.title()}", description=GENERIC_DESCRIPTION, color=EMBED_COLOR)
            embed.set_thumbnail(url=EMBED_THUMBNAIL)
            embed.set_footer(text="Dhab ®")
            channel = bot.get_channel(channel_id)
            await channel.send(embed=embed, view=view)

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
        embed = discord.Embed(title=f"Prices for {realm} (US)", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        prices = get_prices_multi("US")
        for price in prices:
            embed.add_field(name="US Servers", value=price, inline=False)
        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=PandariaView())

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
        embed = discord.Embed(title=f"Prices for {realm} (EU)", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        prices = get_prices_multi("EU")
        for price in prices:
            embed.add_field(name="EU Servers", value=price, inline=False)
        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=PandariaView())

# --------- Pandaria View ---------
class PandariaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PandariaUSDropdown())
        self.add_item(PandariaEUDropdown())

# --------- Retail Buttons ---------
class RetailView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RetailUSButton())
        self.add_item(RetailEUButton())

class RetailUSButton(Button):
    def __init__(self):
        super().__init__(label="WoW Retail US", style=discord.ButtonStyle.green, emoji="🇺🇸")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Price per 100K\nUS Servers", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        prices = get_prices_multi("US")
        for price in prices:
            embed.add_field(name="\u200b", value=price, inline=False)
        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RetailEUButton(Button):
    def __init__(self):
        super().__init__(label="WoW Retail EU", style=discord.ButtonStyle.green, emoji="🇪🇺")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Price per 100K\nEU Servers", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        prices = get_prices_multi("EU")
        for price in prices:
            embed.add_field(name="\u200b", value=price, inline=False)
        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --------- Placeholder Views for Other Games ---------
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
        await interaction.followup.send("Unknown version. Try: pandaria, retail, runescape, poe, albion, classic", ephemeral=True)

load_dotenv()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))