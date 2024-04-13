import aiohttp
import os
import requests
import discord
import config 

key = config.NASA

class NASAButton(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label='APOD', style=discord.ButtonStyle.secondary, custom_id='apod_button', row=1)
    async def apod(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.send_modal(NASAAPODModal(self.bot, self.ctx))
        else:
            await interaction.response.send_message("You can't control these buttons", ephemeral=True)

    @discord.ui.button(label='NEO', style=discord.ButtonStyle.secondary, custom_id='neo_button', row=1)
    async def neo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.send_modal(NASANeoModal(self.bot, self.ctx))
        else:
            await interaction.response.send_message("You can't control these buttons", ephemeral=True)

    @discord.ui.button(label='EPIC', style=discord.ButtonStyle.secondary, custom_id='epic_button', row=1)
    async def date(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.send_modal(NASAModal(self.bot, self.ctx))
        else:
            await interaction.response.send_message("You can't control these buttons", ephemeral=True)

    @discord.ui.button(label='NIVL', style=discord.ButtonStyle.secondary, custom_id='nivl_button', row=1)
    async def nasa_images(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.send_modal(NASANasaImagesModal(self.bot, self.ctx))
        else:
            await interaction.response.send_message("You can't control these buttons", ephemeral=True)

    @discord.ui.button(label='Earth Imagery (Beta)', style=discord.ButtonStyle.secondary, custom_id='earth_imagery_button', row=2)
    async def earth_imagery(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.send_modal(NASAEarthImageryModal(self.bot, self.ctx))
        else:
            await interaction.response.send_message("You can't control these buttons", ephemeral=True)

    @discord.ui.button(emoji='<:Home:1215695139679506553>', style=discord.ButtonStyle.danger, custom_id='home_button', row=2)
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.id == interaction.user.id:
            embed = discord.Embed(title="Access NASA's Database", description="Explore the vast database of NASA using the interactive buttons below.\n\n>>> **APOD** displays the Astronomy Picture of the Day from NASA's API.\n\n**NeoWs (Near Earth Object Web Service)** is a RESTful web service for near earth Asteroid information.\n\n**EPIC** provides information on the daily imagery collected by DSCOVR's Earth Polychromatic Imaging Camera (EPIC) instrument.\n\nUse **NIVL** to access the NASA Image and Video Library site at images.nasa.gov.\n\n**Landsat imagery** is provided to the public as a joint project between NASA and USGS. ", color=0xf4424d)
            embed.set_thumbnail(url="https://i.ibb.co/xmS3KKY/769603815783006228.png")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("You can't control these buttons", ephemeral=True)

class NASAAPODModal(discord.ui.Modal, title='NASA Astronomy Picture of the Day'):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.date_value = discord.ui.TextInput(label='Enter Date', placeholder='YYYY-MM-DD', required=True, style=discord.TextStyle.short, max_length=10)
        self.add_item(self.date_value)

    async def on_submit(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message("You can't control these buttons", ephemeral=True)
        date = self.date_value.value
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.nasa.gov/planetary/apod?date={date}&api_key={key}") as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    data = None

        if data:
            image_url = data['url']
            embed = discord.Embed(title="NASA Astronomy Picture of the Day", description=data['explanation'], color=0xf4424d)
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Date: {date}")
            await interaction.response.edit_message(embed=embed, view=NASAButton(self.bot, self.ctx))
        else:
            await interaction.response.send_message(content="No data found for the provided date", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class NASANeoModal(discord.ui.Modal, title='NASA Near Earth Object'):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.start_date_value = discord.ui.TextInput(label='Enter Start Date', placeholder='YYYY-MM-DD', required=True, style=discord.TextStyle.short, max_length=10)
        self.end_date_value = discord.ui.TextInput(label='Enter End Date', placeholder='YYYY-MM-DD', required=True, style=discord.TextStyle.short, max_length=10)
        self.add_item(self.start_date_value)
        self.add_item(self.end_date_value)

    async def on_submit(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message("You can't control these buttons", ephemeral=True)
        start_date = self.start_date_value.value
        end_date = self.end_date_value.value
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={key}") as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    data = None

        if data:
            neo_count = data['element_count']
            embed = discord.Embed(title="NASA Near Earth Object", description=f"There are **{neo_count}** Near Earth Objects between **{start_date}** and **{end_date}**", color=0xf4424d)
            embed.set_thumbnail(url="https://i.ibb.co/xmS3KKY/769603815783006228.png")
            await interaction.response.edit_message(embed=embed, view=NASAButton(self.bot, self.ctx))
        else:
            await interaction.response.send_message(content="No NEO data found for the provided dates", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class NASAModal(discord.ui.Modal, title='Access EPIC data'):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.date_value = discord.ui.TextInput(label='Enter Date', placeholder='YYYY-MM-DD', required=True, style=discord.TextStyle.short, max_length=10)
        self.add_item(self.date_value)

    async def on_submit(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message("You can't control these buttons", ephemeral=True)
        date = self.date_value.value
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.nasa.gov/EPIC/api/natural/date/{date}?api_key={key}") as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    data = None

        if data:
            image_info = data[0]
            image_url = f"https://api.nasa.gov/EPIC/archive/natural/{date.replace('-', '/')}/png/{image_info['image']}.png?api_key={key}"
            embed = discord.Embed(title="NASA EPIC Data", description=f"{image_info['caption']}\n\n`{image_info['image']}` — `{date}`", color=0xf4424d)         
            embed.set_image(url=image_url)
            embed.add_field(name="Centroid Coordinates", value=f"Lat: {image_info['centroid_coordinates']['lat']}, Lon: {image_info['centroid_coordinates']['lon']}", inline=False)
            embed.add_field(name="DSCVR J2000 Position", value=f"X: {image_info['dscovr_j2000_position']['x']}, Y: {image_info['dscovr_j2000_position']['y']}, Z: {image_info['dscovr_j2000_position']['z']}", inline=False)
            embed.add_field(name="Lunar J2000 Position", value=f"X: {image_info['lunar_j2000_position']['x']}, Y: {image_info['lunar_j2000_position']['y']}, Z: {image_info['lunar_j2000_position']['z']}", inline=False)
            embed.add_field(name="Sun J2000 Position", value=f"X: {image_info['sun_j2000_position']['x']}, Y: {image_info['sun_j2000_position']['y']}, Z: {image_info['sun_j2000_position']['z']}", inline=False)
            embed.add_field(name="Attitude Quaternions", value=f"q0: {image_info['attitude_quaternions']['q0']}, q1: {image_info['attitude_quaternions']['q1']}, q2: {image_info['attitude_quaternions']['q2']}, q3: {image_info['attitude_quaternions']['q3']}", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/xmS3KKY/769603815783006228.png")
            await interaction.response.edit_message(embed=embed, view=NASAButton(self.bot, self.ctx))
        else:
            await interaction.response.send_message(content="No data found for the provided date", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class NASANasaImagesModal(discord.ui.Modal, title='Search NASA Images'):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.query_value = discord.ui.TextInput(label='Enter Query', placeholder='Enter your search query', required=True, style=discord.TextStyle.short)
        self.add_item(self.query_value)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query_value.value.strip()  # Trim leading and trailing spaces
        try:
            response = requests.get(f"https://images-api.nasa.gov/search?q={query}")
            if response.status_code == 200:
                data = response.json()
            else:
                data = None

            if data and data.get('collection', {}).get('items'):
                first_item = data['collection']['items'][0]
                title = first_item['data'][0]['title']
                description = f"{first_item['data'][0]['description']}\n\n**Nasa ID:** {first_item['data'][0]['nasa_id']}\n**Date Created:** {first_item['data'][0]['date_created']}"
                if len(description) > 4000:
                    description = description[:4000] + '...'
                embed = discord.Embed(title=title, description=description, color=0xf4424d)
                if 'links' in first_item:
                    image_url = first_item['links'][0]['href']
                    embed.set_image(url=image_url)
                await interaction.response.edit_message(embed=embed, view=NASAButton(self.bot, self.ctx))
            else:
                await interaction.response.send_message(embed=embed, view=NASAButton(self.bot, self.ctx))
        except Exception as e:
            await interaction.response.send_message(content=f"🤨 Huh, something went wrong? {e}", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

class NASAEarthImageryModal(discord.ui.Modal, title='NASA Earth Imagery'):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.longitude_value = discord.ui.TextInput(label='Enter Longitude', placeholder='Longitude', required=True, style=discord.TextStyle.short)
        self.latitude_value = discord.ui.TextInput(label='Enter Latitude', placeholder='Latitude', required=True, style=discord.TextStyle.short)
        self.date_value = discord.ui.TextInput(label='Enter Date', placeholder='YYYY-MM-DD', required=True, style=discord.TextStyle.short, max_length=10)
        self.add_item(self.longitude_value)
        self.add_item(self.latitude_value)
        self.add_item(self.date_value)

    async def on_submit(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message("You can't control these buttons", ephemeral=True)
        longitude = self.longitude_value.value
        latitude = self.latitude_value.value
        date = self.date_value.value
        image_url = f"https://api.nasa.gov/planetary/earth/imagery?lon={longitude}&lat={latitude}&date={date}&api_key={key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    embed = discord.Embed(title="NASA Earth Imagery", description=f"**Longitude:** {longitude}\n**Latitude:** {latitude}\n**Date:** {date}", color=0xf4424d)
                    embed.set_image(url=image_url)
                    await interaction.response.edit_message(embed=embed, view=NASAButton(self.bot, self.ctx))
                else:
                    await interaction.response.send_message(content="No image found for the provided parameters", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
      