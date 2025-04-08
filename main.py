import re
import socket
import asyncio

from traceback import print_exc

from colors import AuxFG, colorize, get_color_for
from banner import DISPLAY_SERVER_BANNER_B


msg_queue = asyncio.Queue()
writers: set[asyncio.StreamWriter] = set()
taken_usernames = set()


# General utility functions

async def write(writer: asyncio.StreamWriter, data: bytes, ignore_exc=False):
    try:
        writer.write(data)
        await writer.drain()
    except Exception as _:
        if not ignore_exc:
            raise

async def close(writer: asyncio.StreamWriter):
    try:
        writer.close()
        await writer.wait_closed()
    except Exception as _:
        print_exc()


# Writer autoclose decorator

def writer_autoclose(func):
    async def wrapper(*args, **kwargs):
        writer = args[1]
        try:
            await func(*args, **kwargs)
        except Exception as _:
            print_exc()
        await close(writer)
        if writer in writers:
            writers.remove(writer)
    return wrapper


# Client connection callbacks 

@writer_autoclose
async def display_server_cb(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
):
    # Show banner first        
    await write(writer, DISPLAY_SERVER_BANNER_B)

    # Register writer
    writers.add(writer)
    
    # Wait until disconnected
    while True:
        data = await reader.read(1)
        if not data:
            return

@writer_autoclose
async def receive_server_cb(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
):
    # Get username
    await write(
        writer, 
        b"Welcome to the CLUB2 message server!\n"
        b"Please, enter your public username: "
    )
    username = (await reader.readline()).rstrip()
    username_utf8 = username.decode()

    # Check if username contains invalid symbols (b'' case is also accounted!)
    if not re.match(r'^\w+( \w+)*$', username_utf8):
        await write(writer, b"Bad username format\r\n")
        raise ValueError("Bad username format")
    
    # Check username length
    if len(username_utf8) > 30 or len(username_utf8) < 4:
        await write(writer, b"Username length must be from 4 to 30 symbols\r\n")
        raise ValueError(f"Bad username length: got {len(username_utf8)}")

    # Critical section here (sensitive username existance check)
    async with asyncio.Lock():
        if username in taken_usernames:
            await write(writer, b"Username is already taken\r\n")
            raise ValueError("Username is already taken")
        taken_usernames.add(username)
    
    # Small info message
    await write(writer, b"Welcome! Type the message and press Enter twice to send it.\r\n")
    
    # Joined the chat message:
    msg_queue.put_nowait(
        colorize(f"{username_utf8} has joined the chat!", fg=AuxFG.LIGHT_GREEN, bold=True).encode() + b'\r\n'
    )
    
    # Precalculate the colored message prefix byte string
    msg_prefix = colorize(username_utf8, get_color_for(username)).encode() + b': '
    
    try:
        # Message processing loop
        while True:
            data = (await reader.readuntil(b'\n\n'))[:-1]
            if not data:
                return
            msg_queue.put_nowait(msg_prefix + data)
    finally:
        taken_usernames.remove(username)
        msg_queue.put_nowait(
            colorize(f"{username_utf8} has left the chat ._.", fg=AuxFG.RED, bold=False).encode() + b'\r\n'
        )
        

async def main():   
    display_server = await asyncio.start_server(
        client_connected_cb=display_server_cb,
        host="0.0.0.0",
        port=31337,
        family=socket.AF_INET,
    )
    
    receive_server = await asyncio.start_server(
        client_connected_cb=receive_server_cb,
        host="0.0.0.0",
        port=31338,
        family=socket.AF_INET,
    )

    async with receive_server, display_server:
        while True:
            data = await msg_queue.get()
            await asyncio.gather(
                *[write(writer, data, ignore_exc=True) for writer in writers]
            )
                

if __name__ == "__main__":
    asyncio.run(main())


# TODO: Socket send.() raised exception
