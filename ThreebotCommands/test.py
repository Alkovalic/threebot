import Command
import discord
import aiohttp


class TEST(Command.Command):

    async def run(self, client, message):

        with open("christmas.png", "rb") as image:
            await client.edit_profile(avatar=image.read())
