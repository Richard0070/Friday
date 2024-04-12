import json
import os
import discord
import random

WELCOME_JSON_PATH = 'data/welcomer.json'

def load_welcome_channels():
    """
    Load the welcome channel data from a JSON file.
    """
    if os.path.exists(WELCOME_JSON_PATH):
        with open(WELCOME_JSON_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_welcome_channels(welcome_channels):
    """
    Save the welcome channel data to a JSON file.
    """
    os.makedirs(os.path.dirname(WELCOME_JSON_PATH), exist_ok=True)
    with open(WELCOME_JSON_PATH, 'w') as f:
        json.dump(welcome_channels, f)

class WelcomeBtn(discord.ui.View):
    def __init__(self, bot, member, cooldown: int = 60):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member
        self.cooldown = cooldown
        self.cooldown_set = set()
        self.welcome_messages = [
            "Welcome, star! Hope you brought snacks!",
            "Guess who's back? Welcome, legend!",
            "You just made the room 100% cooler! Welcome!",
            "Hope you have insurance, because we're about to have a blast!",
            "You're here! The fun can officially start now!",
            "Welcome! Did you remember to bring cookies?",
            "Hold onto your hat, you're in for a wild ride!",
            "Prepare your jokes; it's time to impress us!",
            "You've just made the best decision of your life! Welcome!",
            "Welcome! You're now legally obligated to tell us a funny story!",
            "Brace yourself; you're about to enter the giggle zone!",
            "Welcome, but be careful—there's no going back!",
            "You're about to become the life of the party! Welcome!",
            "You're here! Now the party can begin!",
            "Welcome! Bring your sense of humor!",
            "You must be the designated comedian—welcome!",
            "Guess who's the guest of honor? Welcome!",
            "Welcome! We've been expecting you... to make us laugh!",
            "Hope your jokes are ready to roll! Welcome!",
            "You're the star we've been waiting for! Welcome!",
            "You're here! Let's break out the dad jokes!",
            "Welcome! Did you remember to pack your sense of adventure?",
            "You just upgraded our awesomeness! Welcome!",
            "We're ready for your best dance moves! Welcome!",
            "Warning: we're highly contagious... with laughter!",
            "Hope your sense of humor is up to date! Welcome!",
            "You're the highlight of the day! Welcome!",
            "We hope you're good at dad jokes—welcome!",
            "You're the human we needed! Welcome!",
            "You've stumbled into the fun zone! Welcome!",
            "Get ready for unforgettable moments! Welcome!",
            "Welcome! Did you bring your laugh track?",
            "You just raised the bar of coolness! Welcome!",
            "Welcome to the mischief club!",
            "You're about to become the punchline of the day! Welcome!",
            "Hope you're ready to be the class clown! Welcome!",
            "You've just unlocked the secret level! Welcome!",
            "Prepare for maximum giggles! Welcome!",
            "You're officially a member of the giggle squad! Welcome!",
            "Ready to break records of fun? Welcome!",
            "Welcome! Our laughter just hit 11/10!",
            "Get ready for some shenanigans! Welcome!",
            "You just walked into a laughter zone! Welcome!",
            "Welcome! You're the MVP—Most Valuable Prankster!",
            "You're in for a giggle fest! Welcome!",
            "The party was waiting for you! Welcome!",
            "We brought the laughs; you bring the fun! Welcome!",
            "Hope you're ready to become a meme! Welcome!",
            "You're the cherry on top of our fun sundae! Welcome!",
            "You're about to learn what real fun looks like! Welcome!",
            "Welcome! Did you bring the jokes?",
            "You're now part of our comedy troupe! Welcome!",
            "Welcome! The giggles are now in your hands!",
            "We heard you're good at puns—welcome!",
            "Welcome! Hope you have the best one-liners!",
            "We're ready for your funniest quips! Welcome!",
            "Get ready to turn up the humor! Welcome!",
            "Hope you have a pocketful of jokes! Welcome!",
            "Ready to become the life of the party? Welcome!",
            "Welcome! We can't wait to see your comedic genius!",
            "You're now the king/queen of the comedy club! Welcome!",
            "Your fun meter just skyrocketed! Welcome!",
            "Welcome! Let's hear your stand-up routine!",
            "You just joined the best comedy show! Welcome!",
            "Hope you're a prank master—welcome!",
            "You're now in the comedy hall of fame! Welcome!",
            "We expect great things from you! Welcome!",
            "Your presence is required for peak fun! Welcome!",
            "Get ready for non-stop laughter! Welcome!"
        ]

    @discord.ui.button(label="Wave", style=discord.ButtonStyle.secondary, emoji="<a:wavey:1228242532681383967>", custom_id='wave')
    async def wave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.cooldown_set:
            await interaction.response.send_message("Calm down, Jamal 😂", ephemeral=True)
            return
        await interaction.response.defer()
        channel = interaction.channel
        webhook = discord.utils.get(await channel.webhooks(), name="Welcomer")
        if not webhook:
            webhook = await channel.create_webhook(
                name=interaction.user.display_name,
                avatar=await interaction.user.avatar.read()
            )
        welcome_message = random.choice(self.welcome_messages)
        await webhook.send(f"{self.member.mention} {welcome_message}",
                           username=interaction.user.display_name,
                           avatar_url=interaction.user.display_avatar.url)
        await webhook.delete()
        self.cooldown_set.add(interaction.user.id)
        asyncio.create_task(self.remove_from_cooldown(interaction.user.id))

    async def remove_from_cooldown(self, user_id: int):
        await asyncio.sleep(self.cooldown)
        self.cooldown_set.remove(user_id)
        