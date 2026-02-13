import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
from typing import Optional

INVITE_LINK = "Our discord jn reminder (for distribution)" 

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.command_cooldowns = {} 

    async def setup_hook(self):
        try:
            await self.tree.sync()
            print("Commands synced successfully.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    await bot.setup_hook()

@bot.tree.command(name="spamcustom", description="Sends your custom message wherever you want")
async def spamcustom(interaction: discord.Interaction, text: str):

    try:
        user_id = interaction.user.id
        cooldown_time = 4

        last_used = bot.command_cooldowns.get(user_id, 0)
        time_since_last_use = time.time() - last_used

        if time_since_last_use < cooldown_time:
            remaining_time = cooldown_time - time_since_last_use

            embed = discord.Embed(
                title="Cooldown Active",
                description=f"Please wait **{remaining_time:.1f} seconds** before using this command again.",
                color=discord.Color.from_rgb(255, 0, 0) 
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        bot.command_cooldowns[user_id] = time.time()

        embed = discord.Embed(
            title="Join Our Discord!",
            description=f"Don't forget to join our community: [Click here to join]({INVITE_LINK})",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        num_responses = 10
        interval_ms = 150
        interval = interval_ms / 1000.0

        for _ in range(num_responses):
            await asyncio.sleep(interval)
            await interaction.followup.send(text, ephemeral=False)

    except discord.Forbidden:
        print("The bot lacks permissions to send messages.")
    except discord.HTTPException as e:
        print(f"HTTP error occurred")
    except Exception as e:
        print(f"Unexpected error")

COLOR_MAP = {
    "red": discord.Color.from_rgb(255, 0, 0),
    "blue": discord.Color.from_rgb(0, 100, 255),
    "green": discord.Color.from_rgb(0, 200, 0),
    "yellow": discord.Color.from_rgb(255, 255, 0),
    "purple": discord.Color.from_rgb(160, 0, 255),
    "orange": discord.Color.from_rgb(255, 165, 0),
}

@bot.tree.command(name="sendembed", description="Sends an embed with your message, a color, and an optional file")
@app_commands.describe(
    message="The message to include in the embed",
    color="Choose the embed color",
    file="Optional file to attach"
)
@app_commands.choices(color=[
    app_commands.Choice(name="Red", value="red"),
    app_commands.Choice(name="Blue", value="blue"),
    app_commands.Choice(name="Green", value="green"),
    app_commands.Choice(name="Yellow", value="yellow"),
    app_commands.Choice(name="Purple", value="purple"),
    app_commands.Choice(name="Orange", value="orange"),
])
async def sendembed(
    interaction: discord.Interaction,
    message: str,
    color: app_commands.Choice[str],
    file: Optional[discord.Attachment] = None
):
    try:
        embed_color = COLOR_MAP.get(color.value, discord.Color.from_rgb(255, 255, 255))

        embed = discord.Embed(
            title="Message",
            description=message,
            color=embed_color
        )


        file_to_send = None
        if file:
            file_to_send = await file.to_file()

        if file_to_send:
            await interaction.response.send_message(embed=embed, file=file_to_send)
        else:
            await interaction.response.send_message(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message("I don't have permissions to send messages here.", ephemeral=True)
    except discord.HTTPException as e:
        print(f"HTTP error: {e}")
        await interaction.response.send_message("An error occurred while sending the embed.", ephemeral=True)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await interaction.response.send_message("Something went wrong.", ephemeral=True)

token = input("Enter your bot token: ")
bot.run(token)
