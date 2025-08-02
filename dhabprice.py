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
albion_sheet = client.open("Classic Price Bot").worksheet("Albion")

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
        self.add_item(AlbionDropdown())

class AlbionDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Europe", emoji="🇪🇺"),
            discord.SelectOption(label="USA", emoji="🇺🇸"),
            discord.SelectOption(label="Asia", emoji="🌏")
        ]
        super().__init__(placeholder="🛒┋ Albion Silver Price - Click here", options=options)

    async def callback(self, interaction: discord.Interaction):
        region = self.values[0].lower()
        price = None

        if region == "europe":
            price = albion_sheet.acell("A2").value
        elif region == "usa":
            price = albion_sheet.acell("B2").value
        elif region == "asia":
            price = albion_sheet.acell("C2").value

        embed = discord.Embed(title=f"Albion Silver Price - {region.title()}", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        if price:
            embed.add_field(name="PER 1M", value=f"{price}$ USD", inline=False)
        else:
            embed.add_field(name="Error", value="Price not found.", inline=False)

        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=AlbionView())


class ClassicFreshDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Spineshatter", emoji="🇪🇺"),
            discord.SelectOption(label="Thunderstrike", emoji="🇪🇺"),
            discord.SelectOption(label="Nightslayer", emoji="🇺🇸"),
            discord.SelectOption(label="Dreamscythe", emoji="🇺🇸"),
            discord.SelectOption(label="Maladath", emoji="🇺🇸")
        ]
        super().__init__(placeholder="Classic Fresh Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]
        region = "US"

        # Row-specific logic for Classic Fresh
        row_map = {
            "Spineshatter": (26, 27),
            "Thunderstrike": (28, 29),
            "Nightslayer": (20, 21),
            "Dreamscythe": (22, 23),
            "Maladath": (24, 25),
        }

        start_row, end_row = row_map.get(realm, (None, None))
        records = sheet.get_all_values()[start_row - 1:end_row]
        embed = discord.Embed(title=f"{realm} - Classic Fresh", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        for row in records:
            if len(row) >= 8:
                faction = row[4]  # Column E
                price = row[7]    # Column H
                if faction and price:
                    embed.add_field(name=f"{faction} - {realm}", value=f"{price}$ USD / 1K", inline=False)

        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=ClassicWoWView())

class SoDUSDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Wild Growth", emoji="🇺🇸"),
            discord.SelectOption(label="Crusader strike", emoji="🇺🇸")
        ]
        super().__init__(placeholder="Season of Discovery US", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]

        row_map = {
            "Wild Growth": (6, 7),
            "Crusader strike": (8, 9),
        }

        start_row, end_row = row_map.get(realm, (None, None))
        records = sheet.get_all_values()[start_row - 1:end_row]

        embed = discord.Embed(title=f"{realm} - SoD US", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        for row in records:
            if len(row) >= 8:
                faction = row[4]  # Column E
                price = row[7]    # Column H
                if faction and price:
                    embed.add_field(name=f"{faction} - {realm}", value=f"{price}$ USD / 1K", inline=False)

        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=ClassicWoWView())

class SoDEUDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Living Flame", emoji="🇪🇺"),
            discord.SelectOption(label="Wild Growth", emoji="🇪🇺")
        ]
        super().__init__(placeholder="Season of Discovery EU", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]

        row_map = {
            "Living Flame": (2, 3),
            "Wild Growth": (4, 5),
        }

        start_row, end_row = row_map.get(realm, (None, None))
        records = sheet.get_all_values()[start_row - 1:end_row]

        embed = discord.Embed(title=f"{realm} - SoD EU", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        for row in records:
            if len(row) >= 8:
                faction = row[4]  # Column E
                price = row[7]    # Column H
                if faction and price:
                    embed.add_field(name=f"{faction} - {realm}", value=f"{price}$ USD / 1K", inline=False)

        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=ClassicWoWView())

class ClassicERADropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Firemaw", emoji="🇪🇺"),
            discord.SelectOption(label="Whitemane", emoji="🇺🇸")
        ]
        super().__init__(placeholder="Classic ERA Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]
        region = "EU" if realm == "Firemaw" else "US"
        results = get_prices(realm, region)
        embed = discord.Embed(title=f"{realm} - Classic ERA", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        for faction in ["Horde", "Alliance"]:
            price = results.get(faction)
            if price:
                embed.add_field(name=f"{faction} - {realm}", value=f"{price}$ USD / 1K", inline=False)
        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=ClassicWoWView())

class HardcoreDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="DoomHowl", emoji="🇺🇸"),
            discord.SelectOption(label="Stitches", emoji="🇪🇺"),
            discord.SelectOption(label="Soulseeker", emoji="🇪🇺")
        ]
        super().__init__(placeholder="Hardcore Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        realm = self.values[0]

        row_map = {
            "DoomHowl": (16, 17),
            "Stitches": (10, 11),
            "Soulseeker": (18, 19),
        }

        start_row, end_row = row_map.get(realm, (None, None))
        records = sheet.get_all_values()[start_row - 1:end_row]

        embed = discord.Embed(title=f"{realm} - Hardcore", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        for row in records:
            if len(row) >= 8:
                faction = row[4]  # Column E
                price = row[7]    # Column H
                if faction and price:
                    embed.add_field(name=f"{faction} - {realm}", value=f"{price}$ USD / 1K", inline=False)

        embed.add_field(name="Open a ticket:", value="<#1361488242792333392>", inline=False)
        embed.set_footer(text="Dhab ®")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.edit(view=ClassicWoWView())

class ClassicWoWView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ClassicFreshDropdown())
        self.add_item(SoDUSDropdown())
        self.add_item(SoDEUDropdown())
        self.add_item(ClassicERADropdown())
        self.add_item(HardcoreDropdown())

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