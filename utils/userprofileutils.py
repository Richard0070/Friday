import discord
import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO

async def create_user_info_image(user: discord.User):
  
    image_path = None
    base_image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "profile_base.png")
    base_image = Image.open(base_image_path)

    if user.bot:
        accent_color = (88, 101, 242)
    else:
        accent_color = user.accent_color.to_rgb()

    base_image = replace_colors(base_image, (29, 29, 29), accent_color)

    font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "ggfont.woff")
    font1 = ImageFont.truetype(font_path, 68)
    font2 = ImageFont.truetype(font_path, 48)

    draw = ImageDraw.Draw(base_image)

    draw.text((120, 500), f"{user.display_name}", fill="white", font=font1)
    draw.text((120, 580), f"{user.name}", fill="#dddddd", font=font2)

    avatar = await get_user_avatar(user)
    avatar = avatar.resize((300, 300))

    mask = Image.new("L", (300, 300), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 300, 300), fill=255)
    avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar.putalpha(mask)

    base_image.paste(avatar, (110, 150), mask=avatar)

    badges_path = os.path.join(os.path.dirname(__file__), "..", "assets")
    badges = user.public_flags.all()
    if badges:  # Check if the user has any badges
        badge_size = 60
        x_offset = base_image.width - 40
        for badge in badges:
            badge_name = badge.name.lower()
            badge_image_path = os.path.join(badges_path, f"{badge_name}.png")
            if os.path.exists(badge_image_path):
                badge_image = Image.open(badge_image_path)
                badge_image = badge_image.resize((badge_size, badge_size))
                x_offset -= (badge_size + 30)
                base_image.paste(badge_image, (x_offset, 400))

    image_path = os.path.join(os.path.dirname(__file__), "..", "userinfo.png")
    base_image.save(image_path)
    return image_path

async def get_user_avatar(user: discord.User):
    if user.avatar:
        avatar_url = user.avatar.url
    else:
        avatar_url = user.default_avatar.url

    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content))
    return avatar

def replace_colors(image, old_color, new_color, tolerance=10):
    data = image.getdata()
    new_data = []
    for item in data:
        if all(abs(c - o) < tolerance for c, o in zip(item[:3], old_color)):
            new_data.append(new_color)
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image
