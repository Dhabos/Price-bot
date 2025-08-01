import discord
from discord.ext import commands
import gspread
from dotenv import load_dotenv
import os
from oauth2client.service_account import ServiceAccountCredentials
from discord.ui import View, Select, Button

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
    guild = discord.Object(id=1400517495294525575)  # Your test server ID
    await bot.tree.sync(guild=guild)
    print(f"Synced slash commands to test server: {guild.id}")
    print(f"Logged in as {bot.user}")

# --------- Pandaria WoW ---------
class PandariaUSDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=s, emoji="🇺🇸") for s in [
                "Benediction", "Grobbulus", "Mankrik", "Whitemane",
                "Faerlina", "Pagle", "Bloodsail Buccaneers", "Atiesh", "Arugal"
            ]
        ]
        super().__init__(placeholder="🇺🇸 ┋ US Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]
        region = "US"
        results = get_prices(realm, region)

        embed = discord.Embed(title=f"Server Prices for {realm}", color=discord.Color.purple())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/968858528343285820/1022583408343384104/dhabava.gif")

        for faction in ["Horde", "Alliance"]:
            price = results.get(faction)
            if price:
                embed.add_field(name=f"{realm} {faction}", value=f"{price}$ USD 🇺🇸", inline=False)

        embed.add_field(name="Open a ticket", value="<#1400825204749635684> | `open-ticket`", inline=False)
        embed.set_footer(text="Dhab ®")

        await interaction.response.edit_message(embed=embed, view=PandariaView())

class PandariaEUDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=s, emoji="🇪🇺") for s in [
                "Gehennas", "Firemaw", "Golemagg", "Pyrewood Village",
                "Mirage Raceway", "Everlook", "Venoxis", "Lakeshire",
                "Sulfuron", "Auberdine", "Mandokir"
            ]
        ]
        super().__init__(placeholder="🇪🇺 ┋ EU Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]
        region = "EU"
        results = get_prices(realm, region)

        embed = discord.Embed(title=f"Server Prices for {realm} (EU)", color=discord.Color.purple())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/968858528343285820/1022583408343384104/dhabava.gif")

        for faction in ["Horde", "Alliance"]:
            price = results.get(faction)
            if price:
                embed.add_field(name=f"{realm} {faction}", value=f"{price}$ USD 🇪🇺", inline=False)

        embed.add_field(name="Open a ticket", value="<#1400825204749635684> | `open-ticket`", inline=False)
        embed.set_footer(text="Dhab ®")

        await interaction.response.edit_message(embed=embed, view=PandariaView())

class PandariaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PandariaUSDropdown())
        self.add_item(PandariaEUDropdown())

# --------- Classic WoW Dropdowns ---------
class ClassicFreshDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Spineshatter", description="EU", emoji="🇪🇺"),
            discord.SelectOption(label="Thunderstrike", description="EU", emoji="🇪🇺"),
            discord.SelectOption(label="Dreamslayer", description="US", emoji="🇺🇸"),
            discord.SelectOption(label="Dreamscythe", description="US", emoji="🇺🇸"),
            discord.SelectOption(label="Maladath", description="US", emoji="🇺🇸")
        ]
        super().__init__(placeholder="Classic Fresh", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You selected {self.values[0]}", ephemeral=True)
        await interaction.message.edit(view=ClassicDropdownView())

class HardcoreDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Defias Pillager", description="US", emoji="🇺🇸"),
            discord.SelectOption(label="Doomhowl", description="US", emoji="🇺🇸"),
            discord.SelectOption(label="Soulseeker", description="EU", emoji="🇪🇺"),
            discord.SelectOption(label="Stitches", description="EU", emoji="🇪🇺")
        ]
        super().__init__(placeholder="Hardcore", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You selected {self.values[0]}", ephemeral=True)
        await interaction.message.edit(view=ClassicDropdownView())

class SodEUDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Wild Growth", description="EU", emoji="🇪🇺"),
            discord.SelectOption(label="Living Flame", description="EU", emoji="🇪🇺")
        ]
        super().__init__(placeholder="SoD EU", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You selected {self.values[0]}", ephemeral=True)
        await interaction.message.edit(view=ClassicDropdownView())

class SodUSDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Wild Growth", description="US", emoji="🇺🇸"),
            discord.SelectOption(label="Crusader Strike", description="US", emoji="🇺🇸")
        ]
        super().__init__(placeholder="SoD US", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You selected {self.values[0]}", ephemeral=True)
        await interaction.message.edit(view=ClassicDropdownView())

class ClassicEraDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Firemaw", description="EU", emoji="🇪🇺"),
            discord.SelectOption(label="Whitemane", description="US", emoji="🇺🇸")
        ]
        super().__init__(placeholder="Classic ERA", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You selected {self.values[0]}", ephemeral=True)
        await interaction.message.edit(view=ClassicDropdownView())

# --------- Classic WoW View ---------
class ClassicDropdownView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ClassicFreshDropdown())
        self.add_item(HardcoreDropdown())
        self.add_item(SodEUDropdown())
        self.add_item(SodUSDropdown())
        self.add_item(ClassicEraDropdown())

# --------- Retail WoW ---------
class RetailButton(Button):
    def __init__(self, label, emoji, region):
        super().__init__(label=label, style=discord.ButtonStyle.success, emoji=emoji)
        self.region = region

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Showing retail WoW prices for {self.region} region...",
            ephemeral=True
        )
        await interaction.message.edit(view=RetailView())

class RetailView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RetailButton(label="WoW Retail US", emoji="🇺🇸", region="US"))
        self.add_item(RetailButton(label="WoW Retail EU", emoji="🇪🇺", region="EU"))

# --------- Runescape ---------
class RunescapeButton(Button):
    def __init__(self, label, emoji, version):
        super().__init__(label=label, style=discord.ButtonStyle.success, emoji=emoji)
        self.version = version

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Showing RuneScape prices for {self.version}...", ephemeral=True)
        await interaction.message.edit(view=RunescapeView())

class RunescapeView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RunescapeButton(label="OSRS", emoji="<:OSRS:1400800119879630899>", version="OSRS"))
        self.add_item(RunescapeButton(label="RS3", emoji="<:rs3:1400800017400205373>", version="RS3"))

# --------- Path of Exile ---------
class POEDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Standard", emoji="💎"),
            discord.SelectOption(label="League", emoji="🔥"),
            discord.SelectOption(label="Hardcore", emoji="💀")
        ]
        super().__init__(placeholder="🛒┋ Path of Exile Currency - Click here", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"POE prices for {self.values[0]} mode.", ephemeral=True)
        await interaction.message.edit(view=POEView())

class POEView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(POEDropdown())

# --------- Albion ---------
class AlbionDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Europe", emoji="🇪🇺"),
            discord.SelectOption(label="USA", emoji="🇺🇸"),
            discord.SelectOption(label="Asia", emoji="🌏")
        ]
        super().__init__(placeholder="🛒┋ Albion Silver Price - Click here", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Albion Silver prices for {self.values[0]} region", ephemeral=True)
        await interaction.message.edit(view=AlbionView())

class AlbionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AlbionDropdown())

from typing import Literal

# --------- Slash Commands for Menus ---------

@bot.tree.command(name="menu", description="Open the price menu for a specific game")
@discord.app_commands.describe(version="Which menu to show (pandaria, retail, runescape, poe, albion, classic)")
async def menu(interaction: discord.Interaction, version: Literal["pandaria", "retail", "runescape", "poe", "albion", "classic"]):
    version = version.lower()

    if version == "pandaria":
        embed = discord.Embed(
            title="**Pandaria WoW Gold**",
            description="Select your region and server below to view prices.\n\nClick here to sell: <#1400825204749635684> | `open-ticket`\nClick here to view payment options: <#1361488179856937122> | `payment`",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/968858528343285820/1022583408343384104/dhabava.gif")
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, view=PandariaView(), ephemeral=False)

    elif version == "retail":
        await interaction.response.send_message("Retail WoW", view=RetailView(), ephemeral=False)
    elif version == "runescape":
        await interaction.response.send_message("RuneScape Gold", view=RunescapeView(), ephemeral=False)
    elif version == "poe":
        await interaction.response.send_message("Path of Exile Currency", view=POEView(), ephemeral=False)
    elif version == "albion":
        await interaction.response.send_message("Albion Silver", view=AlbionView(), ephemeral=False)
    elif version == "classic":
        await interaction.response.send_message("Classic WoW", view=ClassicDropdownView(), ephemeral=False)
    else:
        await interaction.response.send_message("Unknown version. Please try one of: pandaria, retail, runescape, poe, albion, classic", ephemeral=True)

load_dotenv()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))