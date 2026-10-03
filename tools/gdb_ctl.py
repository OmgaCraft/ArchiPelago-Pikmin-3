"""
Pilote la session de débogage persistante (tools/gdb_session.py).

Exemples :
    py -3.13 tools/gdb_ctl.py status
    py -3.13 tools/gdb_ctl.py watch 0x34A4D7AC            (écriture, 4 octets)
    py -3.13 tools/gdb_ctl.py watch 0x34A4D7B0 --kind access
    py -3.13 tools/gdb_ctl.py unwatch
    py -3.13 tools/gdb_ctl.py break 0x0309AC84
    py -3.13 tools/gdb_ctl.py unbreak 0x0309AC84
    py -3.13 tools/gdb_ctl.py limit 20                    (retire tout après 20 arrêts)
    py -3.13 tools/gdb_ctl.py mem 0x34A4D7AC --len 16
    py -3.13 tools/gdb_ctl.py hits --n 10
    py -3.13 tools/gdb_ctl.py raw qfThreadInfo            (paquet GDB brut)
    py -3.13 tools/gdb_ctl.py stop
"""

import argparse
import json
import socket

CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 47001


def main():
    parser = argparse.ArgumentParser(description="Pilote gdb_session.py")
    parser.add_argument("cmd", choices=["status", "watch", "unwatch", "break", "unbreak", "limit", "mem", "hits", "raw", "stop"])
    parser.add_argument("arg", nargs="?", help="Adresse (watch/break/unbreak/mem), nombre (limit) ou paquet GDB (raw)")
    parser.add_argument("--len", default="4")
    parser.add_argument("--kind", default="write", choices=["write", "read", "access"])
    parser.add_argument("--n", default="20")
    args = parser.parse_args()

    request = {"cmd": args.cmd, "len": args.len, "kind": args.kind, "n": args.n}
    if args.arg is not None:
        request["addr"] = args.arg
        request["n"] = args.arg if args.cmd == "limit" else args.n

    with socket.create_connection((CONTROL_HOST, CONTROL_PORT), timeout=30) as sock:
        sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
        raw = b""
        while not raw.endswith(b"\n"):
            chunk = sock.recv(65536)
            if not chunk:
                break
            raw += chunk
    response = json.loads(raw.decode("utf-8"))
    if "hits" in response:
        for hit in response["hits"]:
            fmt = lambda v: f"0x{v:08X}" if isinstance(v, int) else str(v)  # noqa: E731
            print(f"[{hit['time']}] {hit['reason']} PC={fmt(hit['pc'])} LR={fmt(hit['lr'])} r3={fmt(hit['r3'])} "
                  f"valeur={hit['value']} pile=[{', '.join(fmt(x) for x in hit['stack'])}]")
    else:
        print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
