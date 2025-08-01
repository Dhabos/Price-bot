
import discord
from discord.ext import commands
from discord.ui import View, Button, Select

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --------- Retail WoW ---------
class RetailView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RetailButton(label="WoW Retail Rates US", region="US"))
        self.add_item(RetailButton(label="WoW Retail Rates EU", region="EU"))

class RetailButton(Button):
    def __init__(self, label, region):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.region = region

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Showing retail WoW prices for {self.region} region...",
            ephemeral=True
        )
        await interaction.message.edit(view=RetailView())  # Reset view

# --------- Pandaria WoW ---------
class PandariaUSDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=s, emoji="🇺🇸") for s in [
                "Benediction", "Grobbulus", "Mankrik", "Whitemane",
                "Faerlina", "Pagle", "Bloodsail Buccaneers", "Atiesh", "Arugal"
            ]
        ]
        super().__init__(placeholder="🇺🇸 US Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Prices for {self.values[0]} (US)",
            ephemeral=True
        )
        await interaction.message.edit(view=PandariaView())  # Reset view

class PandariaEUDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=s, emoji="🇪🇺") for s in [
                "Gehennas", "Firemaw", "Golemagg", "Pyrewood Village",
                "Mirage Raceway", "Everlook", "Venoxis", "Lakeshire",
                "Sulfuron", "Auberdine", "Mandokir"
            ]
        ]
        super().__init__(placeholder="🇪🇺 EU Servers", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Prices for {self.values[0]} (EU)",
            ephemeral=True
        )
        await interaction.message.edit(view=PandariaView())  # Reset view

class PandariaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PandariaUSDropdown())
        self.add_item(PandariaEUDropdown())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        # Retail WoW Channel
        retail_channel = bot.get_channel(1400517495772811276)
        if retail_channel:
            embed = discord.Embed(
                title="Retail WoW Prices",
                description="Choose your region below to view prices.",
                color=discord.Color.green()
            )
            await retail_channel.send(embed=embed, view=RetailView())

        # Pandaria WoW Channel
        pandaria_channel = bot.get_channel(1400519970743390369)
        if pandaria_channel:
            embed = discord.Embed(
                title="Pandaria WoW Prices",
                description="Select your region and server below.",
                color=discord.Color.blue()
            )
            await pandaria_channel.send(embed=embed, view=PandariaView())
    except Exception as e:
        print(f"Error during on_ready: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.lower() == "!menu":
        await on_ready()
    await bot.process_commands(message)

bot.run("MTQwMDUxNDQwMTAyNjU3MjU3OQ.GrGrs4.7B4VfJle3gZFeAy6RexaxKhyPKUiOciBQMxXGI")
