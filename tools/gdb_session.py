"""
Outil de Phase 0 : session de débogage persistante sur le stub GDB de Cemu.

Le stub de Cemu gère mal les déconnexions (il reste bloqué sur l'ancienne
connexion) : cette session reste donc connectée en permanence et se pilote
à distance avec tools/gdb_ctl.py, sans relancer le jeu.

À chaque arrêt (point d'arrêt d'exécution ou surveillance mémoire), la session
journalise : PC, LR, r1, r3, r4, f1, la valeur surveillée et la pile d'appels
(chaîne des LR sauvegardés, fiable même quand le PC renvoyé par Cemu est
imprécis), puis relance tous les threads (« vCont;c »).

Lancement (jeu démarré avec « Debug -> Launch with GDB Stub ») :
    py -3.13 tools/gdb_session.py --log docs/phase0/logs/gdb_session.log
Pilotage : voir tools/gdb_ctl.py.
"""

import argparse
import json
import os
import re
import select
import socket
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_probe as mp  # noqa: E402

# 127.0.0.2 : Razer Synapse occupe 127.0.0.1:1337 sur cette machine (voir gdb_watch.py).
STUB_HOST = "127.0.0.2"
STUB_PORT = 1337
CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 47001

CONTINUE_ALL = "vCont;c"
# Registres lus à chaque arrêt. Pas de registre flottant ni de lecture mémoire via le
# stub : une lecture à une adresse invalide peut faire planter Cemu (constaté le
# 2026-09-28). La mémoire est lue directement dans le processus (memory_probe).
REG_R1, REG_R3, REG_R4 = 1, 3, 4
REG_PC, REG_LR = 64, 67
STACK_DEPTH = 10
WATCH_KINDS = {"write": 2, "read": 3, "access": 4}


class Stub:
    """Connexion au stub GDB (paquets « $données#somme »)."""

    def __init__(self, host, port):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(None)
        self.buffer = b""

    def _recv_byte(self):
        while not self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Connexion fermée par Cemu")
            self.buffer += chunk
        byte, self.buffer = self.buffer[:1], self.buffer[1:]
        return byte

    def send(self, payload):
        data = payload.encode("ascii")
        self.sock.sendall(b"$" + data + b"#" + f"{sum(data) & 0xFF:02x}".encode("ascii"))
        ack = self._recv_byte()
        if ack != b"+":
            self.buffer = ack + self.buffer

    def recv(self):
        while self._recv_byte() != b"$":
            pass
        payload = b""
        while True:
            byte = self._recv_byte()
            if byte == b"#":
                break
            payload += byte
        self._recv_byte()
        self._recv_byte()
        self.sock.sendall(b"+")
        return payload.decode("ascii", errors="replace")

    def command(self, payload):
        self.send(payload)
        return self.recv()

    def readable(self, timeout):
        if self.buffer:
            return True
        return bool(select.select([self.sock], [], [], timeout)[0])

    def reg(self, number):
        reply = self.command(f"p{number:x}")
        if not reply or reply.startswith("E"):
            return None
        if 32 <= number < 64:
            # Registre flottant : 16 chiffres hex = double, 8 = simple précision
            raw = bytes.fromhex(reply)
            return struct.unpack(">d" if len(raw) == 8 else ">f", raw[:8] if len(raw) >= 8 else raw)[0]
        return int(reply[:8], 16)

    def mem(self, address, length):
        reply = self.command(f"m{address:x},{length:x}")
        if not reply or reply.startswith("E"):
            return None
        return bytes.fromhex(reply)

    def u32(self, address):
        data = self.mem(address, 4)
        return struct.unpack(">I", data)[0] if data and len(data) == 4 else None


class SafeMemory:
    """Lecture mémoire directe dans le processus Cemu : une adresse invalide renvoie None."""

    def __init__(self):
        class ProbeArgs:
            pid = None
            base = None
        self.memory = mp.open_memory(ProbeArgs())

    def mem(self, address, length):
        try:
            return self.memory.read(address, length)
        except OSError:
            return None

    def u32(self, address):
        data = self.mem(address, 4)
        return struct.unpack(">I", data)[0] if data and len(data) == 4 else None


class Session:
    def __init__(self, stub, log_path):
        self.stub = stub
        self.memory = SafeMemory()
        self.log_file = open(log_path, "a", encoding="utf-8") if log_path else None
        self.watch = None            # (adresse, taille, type)
        self.breakpoints = set()     # adresses d'exécution
        self.running = False
        self.hits = []               # derniers arrêts (pour gdb_ctl « hits »)
        self.hit_limit = None        # arrêt automatique après N arrêts (anti-inondation)

    def log(self, line):
        stamped = f"[{time.strftime('%H:%M:%S')}] {line}"
        print(stamped, flush=True)
        if self.log_file:
            self.log_file.write(stamped + "\n")
            self.log_file.flush()

    # --- Pause / reprise ---------------------------------------------------

    def pause(self):
        if not self.running:
            return
        self.stub.sock.sendall(b"\x03")
        self.stub.recv()
        self.running = False

    def resume(self):
        self.stub.send(CONTINUE_ALL)
        self.running = True

    # --- Points d'arrêt ------------------------------------------------------

    def set_watch(self, address, length, kind):
        self.clear_watch()
        reply = self.stub.command(f"Z{WATCH_KINDS[kind]},{address:x},{length:x}")
        if reply == "OK":
            self.watch = (address, length, kind)
        return reply

    def clear_watch(self):
        if self.watch:
            address, length, kind = self.watch
            self.stub.command(f"z{WATCH_KINDS[kind]},{address:x},{length:x}")
            self.watch = None

    def add_break(self, address):
        reply = self.stub.command(f"Z0,{address:x},4")
        if reply == "OK":
            self.breakpoints.add(address)
        return reply

    def del_break(self, address):
        reply = self.stub.command(f"z0,{address:x},4")
        self.breakpoints.discard(address)
        return reply

    # --- Analyse d'un arrêt ------------------------------------------------

    def backtrace(self, sp):
        """Remonte la chaîne des cadres PPC : [sp] = cadre précédent, [cadre+4] = LR sauvegardé."""
        frames = []
        for _ in range(STACK_DEPTH):
            if sp is None or sp == 0 or sp % 4:
                break
            previous = self.memory.u32(sp)
            if previous is None or previous <= sp:
                break
            saved_lr = self.memory.u32(previous + 4)
            if saved_lr:
                frames.append(saved_lr)
            sp = previous
        return frames

    def on_stop(self, reply):
        stub = self.stub
        # Les registres lus par « p » sont ceux du thread « général » (Hg), par défaut
        # PAS celui qui s'est arrêté : on sélectionne d'abord le thread de l'arrêt.
        # (Sans cela, PC/LR/pile venaient d'un autre thread — constaté le 2026-09-28.)
        thread_match = re.search(r"thread:([0-9A-Fa-f]+)", reply)
        if thread_match:
            stub.command(f"Hg{thread_match.group(1)}")
        pc, lr = stub.reg(REG_PC), stub.reg(REG_LR)
        r1, r3, r4 = stub.reg(REG_R1), stub.reg(REG_R3), stub.reg(REG_R4)
        f1 = None
        stack = self.backtrace(r1)
        value = None
        if self.watch:
            data = self.memory.mem(self.watch[0], self.watch[1])
            value = data.hex().upper() if data else None
        reason = re.search(r"(watch|rwatch|awatch|swbreak|hwbreak)", reply)
        hit = {
            "time": time.strftime("%H:%M:%S"),
            "reason": reason.group(1) if reason else reply[:20],
            "pc": pc, "lr": lr, "r1": r1, "r3": r3, "r4": r4, "f1": f1,
            "value": value, "stack": stack, "thread": (re.search(r"thread:([0-9A-Fa-f]+)", reply) or [None, None])[1],
        }
        self.hits.append(hit)
        self.hits = self.hits[-200:]
        fmt = lambda v: f"0x{v:08X}" if isinstance(v, int) else str(v)  # noqa: E731
        self.log(f"ARRÊT {hit['reason']} thread={hit['thread']} PC={fmt(pc)} LR={fmt(lr)} r1={fmt(r1)} "
                 f"r3={fmt(r3)} r4={fmt(r4)} f1={f1} valeur={value} pile=[{', '.join(fmt(x) for x in stack)}]")
        if self.hit_limit is not None:
            self.hit_limit -= 1
            if self.hit_limit <= 0:
                self.log("Limite d'arrêts atteinte : surveillance et points d'arrêt retirés.")
                self.clear_watch()
                for address in list(self.breakpoints):
                    self.del_break(address)
                self.hit_limit = None

    # --- Commandes de pilotage --------------------------------------------

    def handle(self, request):
        cmd = request.get("cmd")
        if cmd == "status":
            return {"running": self.running, "watch": self.watch, "breakpoints": sorted(self.breakpoints)}
        if cmd == "hits":
            return {"hits": self.hits[-int(request.get("n", 20)):]}
        if cmd == "stop":
            return {"stop": True}
        was_running = self.running
        self.pause()
        try:
            if cmd == "watch":
                reply = self.set_watch(int(request["addr"], 0), int(request.get("len", "4"), 0), request.get("kind", "write"))
                result = {"reply": reply}
            elif cmd == "unwatch":
                self.clear_watch()
                result = {"reply": "OK"}
            elif cmd == "break":
                result = {"reply": self.add_break(int(request["addr"], 0))}
            elif cmd == "unbreak":
                result = {"reply": self.del_break(int(request["addr"], 0))}
            elif cmd == "limit":
                self.hit_limit = int(request["n"])
                result = {"reply": "OK"}
            elif cmd == "mem":
                data = self.memory.mem(int(request["addr"], 0), int(request.get("len", "16"), 0))
                result = {"data": data.hex().upper() if data else None}
            elif cmd == "raw":
                # Paquet GDB brut (jeu en pause pendant l'échange), ex. « qfThreadInfo »
                result = {"reply": self.stub.command(request["addr"])}
            else:
                result = {"error": f"commande inconnue : {cmd}"}
        finally:
            if was_running:
                self.resume()
        return result

    def shutdown(self):
        self.log("Fermeture : retrait des points d'arrêt, le jeu continue.")
        try:
            self.pause()
            self.clear_watch()
            for address in list(self.breakpoints):
                self.del_break(address)
            self.resume()
        except (ConnectionError, OSError) as error:
            self.log(f"Nettoyage incomplet : {error}")
        if self.log_file:
            self.log_file.close()


def main():
    parser = argparse.ArgumentParser(description="Session de débogage persistante (stub GDB de Cemu).")
    parser.add_argument("--log", help="Fichier journal")
    args = parser.parse_args()

    stub = Stub(STUB_HOST, STUB_PORT)
    session = Session(stub, args.log)
    session.log(f"Connecté au stub {STUB_HOST}:{STUB_PORT} ; état : {stub.command('?')}")

    control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    control.bind((CONTROL_HOST, CONTROL_PORT))
    control.listen(4)
    session.log(f"Pilotage sur {CONTROL_HOST}:{CONTROL_PORT} (tools/gdb_ctl.py)")

    session.resume()
    try:
        while True:
            if session.running and stub.readable(0):
                reply = stub.recv()
                if reply.startswith(("W", "X")):
                    session.log(f"Le jeu s'est terminé : {reply}")
                    break
                session.running = False
                session.on_stop(reply)
                session.resume()
                continue
            ready = select.select([control, stub.sock], [], [], 0.5)[0]
            if control in ready:
                client, _ = control.accept()
                with client:
                    raw = b""
                    while not raw.endswith(b"\n"):
                        chunk = client.recv(4096)
                        if not chunk:
                            break
                        raw += chunk
                    request = json.loads(raw.decode("utf-8") or "{}")
                    response = session.handle(request)
                    client.sendall((json.dumps(response) + "\n").encode("utf-8"))
                    if response.get("stop"):
                        break
    except KeyboardInterrupt:
        pass
    finally:
        session.shutdown()


if __name__ == "__main__":
    main()
