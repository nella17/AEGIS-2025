#!/usr/bin/env python3
from pwn import *

BIN_PATH = args.BINARY or "./netdiag"

exe = context.binary = BIN_PATH
#  context.log_level = "debug"  # uncomment while developing

HOST, PORT = "192.168.0.211", 1337
if os.getenv("container"):
    HOST = "host.containers.internal"
if os.getenv("SSH_CONNECTION"):
    HOST = "127.0.0.1"
TOKEN = "e0474f5b11ef48439fec9f14c439c514"


def start():
    """
    Start local process or connect to remote if you pass:
      REMOTE=1 HOST=example.com PORT=1337
    Usage examples:
      python3 script.py
      python3 script.py REMOTE=1 HOST=challenge HOST=1337
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
        return process(BIN_PATH)


class NetDiagClient:
    """
    Helper around the 'Network Diagnostics and Monitoring Suite' menu binary.

    Invariant: after each public method returns, the process is left at the
    *main* menu 'Option: ' prompt.
    """

    def __init__(self, io):
        self.io = io
        self._recv_main_menu()

    # ---------- generic helpers ----------

    def _recv_main_menu(self):
        """
        Read until the main menu 'Option: ' prompt appears.
        Returns all data that was received.
        """
        return self.io.recvuntil(b"Option: ")

    def _choose_main(self, num: int):
        """Send a choice at the main menu (expects we are at 'Option: ')."""
        self.io.sendline(str(num).encode())

    def _enter_config_manager(self):
        """
        From the main menu, go into 'Configuration Manager' and stop at its 'Option: '.
        """
        self._choose_main(4)
        # Eat the 'Configuration Manager' header and config menu text
        self.io.recvuntil(b"Configuration Manager")
        return self.io.recvuntil(b"Option: ")

    # ---------- top‑level menu actions ----------

    def ping_custom(
        self,
        host: str | None = None,
        count: int | None = None,
        timeout_ms: int | None = None,
    ):
        """
        1. Ping Host (Custom ICMP)

        host=None / ""  -> just press enter and let the binary use its default gateway
        count=None      -> press enter, use current default ping count
        timeout_ms=None -> press enter, use current default timeout

        Returns: bytes of everything up to the next main 'Option: ' prompt.
        """
        self._choose_main(1)

        # hostname / IP
        self.io.sendlineafter(
            b"Enter hostname or IP address", b"" if host is None else host.encode()
        )

        # ping count
        # if count is None:
        #    self.io.sendlineafter(b"Enter ping count", b"")
        # else:
        #    self.io.sendlineafter(b"Enter ping count", str(count).encode())

        ## timeout ms
        # if timeout_ms is None:
        #    self.io.sendlineafter(b"Enter timeout in ms", b"")
        # else:
        #    self.io.sendlineafter(b"Enter timeout in ms", str(timeout_ms).encode())

        # It will run the custom ICMP ping and then redisplay the main menu
        return self._recv_main_menu()

    def ping_system(
        self,
        host: str | None = None,
        count: int | None = None,
        timeout_ms: int | None = None,
    ):
        """
        2. Ping Host (system ping)

        Uses the system command:
            ping -c <count> -W <timeout_seconds> <host>

        Same semantics for None parameters as ping_custom().

        Returns: bytes up to the next main 'Option: ' prompt.
        """
        self._choose_main(2)

        # hostname / IP
        self.io.sendlineafter(
            b"Enter hostname or IP address", b"" if host is None else host.encode()
        )

        # ping count
        if count is None:
            self.io.sendlineafter(b"Enter ping count", b"")
        else:
            self.io.sendlineafter(b"Enter ping count", str(count).encode())

        # timeout ms
        if timeout_ms is None:
            self.io.sendlineafter(b"Enter timeout in ms", b"")
        else:
            self.io.sendlineafter(b"Enter timeout in ms", str(timeout_ms).encode())

        # The binary executes ping and then goes back to the main menu
        return self._recv_main_menu()

    def generate_report(self, fmt: str | None = None):
        """
        3. Generate Report

        fmt values the binary accepts: "text", "json", "csv".
        fmt=None / "" -> just press enter, use current default report format.

        Returns: bytes up to the next main 'Option: ' prompt.
        """
        self._choose_main(3)

        self.io.sendlineafter(b"Enter report format", b"" if not fmt else fmt.encode())

        # It prints "Generated report in <fmt> format"
        return self._recv_main_menu()

    # ---------- configuration manager (4) ----------

    def config_update_gateway(self, new_gateway: str):
        """
        4 -> 1. Update Default Gateway

        new_gateway: hostname or IP string.
        """
        self._enter_config_manager()
        self.io.sendline(b"1")
        self.io.sendlineafter(
            b"Enter default gateway hostname or IP", new_gateway.encode()
        )
        # Goes back to main menu
        return self._recv_main_menu()

    def config_update_ping_count(self, new_count: int):
        """
        4 -> 2. Update Ping Count

        new_count: 1–100
        """
        self._enter_config_manager()
        self.io.sendline(b"2")
        self.io.sendlineafter(b"Enter default ping count", str(new_count).encode())
        return self._recv_main_menu()

    def config_update_timeout(self, new_timeout_ms: int):
        """
        4 -> 3. Update Timeout (in ms)

        new_timeout_ms: 100–5000
        """
        self._enter_config_manager()
        self.io.sendline(b"3")
        self.io.sendlineafter(
            b"Enter default timeout in ms", str(new_timeout_ms).encode()
        )
        return self._recv_main_menu()

    def config_update_report_format(self, new_fmt: str):
        """
        4 -> 4. Update Report Format

        new_fmt: "text", "json", or "csv"
        """
        self._enter_config_manager()
        self.io.sendline(b"4")
        self.io.sendlineafter(b"Enter report format", new_fmt.encode())
        return self._recv_main_menu()

    def config_update_log_level(self, lvl: str):
        """
        4 -> 5. Update Log Level

        lvl: "debug", "info", or "error"
        """
        self._enter_config_manager()
        self.io.sendline(b"5")
        self.io.sendafter(b"Enter log level", lvl.encode())
        return self._recv_main_menu()

    def config_list(self):
        """
        4 -> 6. List Current Configurations

        Returns the block that includes the "Current Configurations:" section
        *plus* the following main menu that shows up.
        """
        self._enter_config_manager()
        self.io.sendline(b"6")

        # Read until the main menu comes back
        data = self.io.recvuntil(b"Network Diagnostics and Monitoring Suite")
        # plus the rest of the menu up to 'Option: '
        data += self.io.recvuntil(b"Option: ")
        return data

    # ---------- exit ----------

    def quit(self):
        """
        5. Exit

        Returns: everything until EOF.
        """
        self._choose_main(5)
        return self.io.recvall()


if __name__ == "__main__":
    io = start()
    nd = NetDiagClient(io)

    nd.ping_custom(host=None, count=None, timeout_ms=None)

    nd.ping_system(host="127.0.0.1", count=1, timeout_ms=500)

    nd.generate_report("text")

    nd.config_update_gateway("1.1.1.1")
    nd.config_update_ping_count(1)
    nd.config_update_timeout(100)
    nd.config_update_report_format("text")
    nd.config_update_log_level("debug")

    for i in range(0x100):
        nd.ping_system(host="127.0.0.1", count=1, timeout_ms=100)

    # cfg = nd.config_list()
    # print(cfg.decode(errors="ignore"))
    io.interactive()
    # 6. Cleanly exit
    nd.quit()
