import asyncio

from discord.ext import commands
from . import archive


# Cog
class ARC:

    def __init__(self, bot):
        self._bot = bot
        self._arc_manager = None

    async def on_ready(self):

        while not self._bot.pool:
            await asyncio.sleep(delay=1, loop=self._bot.loop)

        self._arc_manager = archive.Archive(self._bot)

    @commands.group(help="Archive system that uses a key -> value layout to access saved items.\n"
                         "Use arc <key> to access a value.",
                    brief="- Archive system.")
    async def archive(self, ctx):
        if ctx.invoked_subcommand is None:

            # TODO:  USE THIS AS AN ON_MESSAGE FOR GETTING ARC ENTRIES?
            print(ctx.message.content)

            # Otherwise, return usage information.
            return await ctx.send(f"Type {self._bot.command_prefix}help archive for usage.")

    @archive.command(name="add",
                 help="Adds a <name>:<data> association to the archive.\n"
                      "If a message ID is passed as <data>, "
                      "Threebot will attempt to find the message and add it as the content instead.\n"
                      "If no <data> is passed, the user has 20 seconds to upload a file to associate with the name.\n"
                      "  Notes:  If the file is larger than 8 MB, it will not be added to the archive.\n"
                      "          If the file already exists, the <name> will be returned, "
                      "and the association will not be made.\n"
                      "          Adding a sound file to the archive will add it to the soundboard.",
                 brief="- Creating name associations.")
    async def add(self, ctx, name, data=None):

        value = data
        
        # Handle case where no data entry was passed.
        if not data:

            # Begin seeking for a file.
            await ctx.send(f"Please upload a file, {ctx.author.name}.")

            # A lot of this is straight from the documentation, so thanks, Rapptz.
            
            # check returns whether a message has attachments, and the attatchment is less than 8mb.
            def check(m):
                return bool(m.attachments) and (m.attachments[0].size < 8000000)

            msg = None
            try:  # Wait for a message with an attachment.
                msg = await self._bot.wait_for('message', check=check, timeout=20.0)
            except asyncio.TimeoutError:  # 20 seconds has passed without a valid file sent.
                return await ctx.send("File not found, or file was too big!")
            else:

                # A valid file has been sent at this point.
                value = msg.attachments[0]
        
        try:
            await self._arc_manager.add_entry(name, ctx.author.name, ctx.guild.id, self._bot.get_table_name(ctx.guild.id), value)
            return await ctx.send(f'Entry "{name}" added!')
        except ValueError as v:  # Entry failed due to an invalid value being passed.
            return await ctx.send(v.args[0])
        except FileExistsError as f:  # Entry failed due to an association or file already existing.
            return await ctx.send(f'Entry "{f.args[0]}" already exists!')

    @archive.command(name="rm",
                 help="Removes a <name>:<data> association from the archive.\n"
                      "The author must either be the creator of the association, "
                      "or must have an administrative role.\n"
                      "Returns the data after removing the association.",
                 brief="- Removing name associations.")
    async def rm(self, ctx, name):
        print(f"removing {name}")


def setup(bot):
    bot.add_cog(ARC(bot))
