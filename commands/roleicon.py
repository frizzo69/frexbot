import discord
from discord.ext import commands
import aiohttp
import re

class RoleIcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roleicon", aliases=["seticon", "ri"])
    @commands.has_permissions(manage_roles=True)
    async def role_icon(self, ctx, role: discord.Role, emoji_or_url: str = None):
        """
        Sets a role icon.
        Usage:
        -roleicon @Role (Attach image)
        -roleicon @Role <Emoji>
        -roleicon @Role <URL>
        """

        # Check if the server has enough boosts (Level 2 required for icons)
        if ctx.guild.premium_tier < 2:
            await ctx.send("⚠️ **Warning:** This server is not Level 2 Boosted. Role icons might not update.")

        # --- CASE 1: Attachment (Image Upload) ---
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
            await self.set_role_image(ctx, role, url)
            return

        if not emoji_or_url:
            await ctx.send("❌ Please provide a Role and either an image, emoji, or URL.")
            return

        # --- CASE 2: Custom Emoji (<:name:id>) ---
        # We extract the ID to get the image link
        custom_emoji_match = re.search(r'<a?:.+:(\d+)>', emoji_or_url)
        if custom_emoji_match:
            emoji_id = custom_emoji_match.group(1)
            is_animated = emoji_or_url.startswith('<a:')
            ext = 'gif' if is_animated else 'png'
            
            # Construct the CDN URL
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=256"
            await self.set_role_image(ctx, role, url)
            return

        # --- CASE 3: Standard Unicode Emoji (👑, 🔥, etc.) ---
        # We try to set this as a 'unicode_emoji' directly
        if self.is_unicode_emoji(emoji_or_url):
            try:
                await role.edit(unicode_emoji=emoji_or_url)
                await ctx.send(f"✅ **Success!** Set {role.mention} icon to: {emoji_or_url}")
                return
            except discord.HTTPException as e:
                # If this fails, it might be a URL disguised as text
                print(f"Not a unicode emoji, trying URL... ({e})")

        # --- CASE 4: Direct URL String ---
        # If it wasn't a standard emoji, we assume it's a link to an image
        await self.set_role_image(ctx, role, emoji_or_url)

    async def set_role_image(self, ctx, role, url):
        """Downloads image from URL and applies it to the role."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Could not download the image. Check the URL.")
                        return
                    data = await resp.read()
            
            # 'display_icon' is the parameter for image-based icons
            await role.edit(display_icon=data)
            await ctx.send(f"✅ **Success!** Role icon updated for {role.mention}.")
            
        except discord.Forbidden:
            await ctx.send("❌ **Permission Error:** I cannot edit this role (it might be above me) or the server lacks Level 2 Boosts.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ **API Error:** {e}")
        except Exception as e:
            await ctx.send(f"❌ **Error:** {e}")

    def is_unicode_emoji(self, s):
        """Simple check to see if a string is likely a standard emoji"""
        # This is a basic check; if it's not a URL and not a custom emoji, we assume unicode
        return not s.startswith("http") and not re.match(r'<a?:.+:(\d+)>', s)

async def setup(bot):
    await bot.add_cog(RoleIcon(bot))
