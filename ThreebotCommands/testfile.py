import Command


class MEME(Command.Command):

    async def run(self, client, message):
        return await client.send_message("im gay")
