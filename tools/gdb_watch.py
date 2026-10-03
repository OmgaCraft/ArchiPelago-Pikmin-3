"""
Outil de Phase 0 : surveille des adresses Wii U via le stub GDB de Cemu et
journalise l'instruction du jeu qui les modifie.

Prérequis : lancer le jeu avec « Debug -> Launch with GDB Stub » (port 1337 par
défaut, réglable dans les options de Cemu). Le jeu attend qu'un débogueur se
connecte : cet outil se connecte, pose les points d'arrêt en écriture, puis
relance le jeu. À chaque écriture surveillée, il affiche l'adresse, la nouvelle
valeur, le PC et le LR (adresse de retour), puis relance automatiquement.

Protocole : GDB Remote Serial Protocol (paquets « $données#somme »).
Aucune dépendance externe.

Exemples :
    py -3.13 tools/gdb_watch.py 0x34A4D7AC:4 0x34A4D7B0:4
    py -3.13 tools/gdb_watch.py 0x34A4D7AC:4 --log docs/phase0/watch_jus.log
"""

import argparse
import os
import re
import select
import socket
import struct
import sys
import time

# 127.0.0.2 et non 127.0.0.1 : sur cette machine, Razer Synapse (RzSDKServer) écoute
# déjà sur 127.0.0.1:1337, alors que Cemu écoute sur 0.0.0.0:1337. Une connexion à
# 127.0.0.1 arrive donc chez Razer ; 127.0.0.2 (autre adresse de bouclage) arrive chez Cemu.
DEFAULT_HOST = "127.0.0.2"
DEFAULT_PORT = 1337

# Numéros de registres PowerPC dans GDB (cible rs6000/powerpc standard).
# À confirmer avec Cemu : en cas d'échec, on retombe sur le paquet « g ».
REG_PC = 64
REG_LR = 67

# Relance de TOUS les threads : avec Cemu, « c » ne relance que le thread par défaut
# (les autres restent suspendus et le jeu reste figé). « vCont;c » cible tous les threads.
CONTINUE_ALL = "vCont;c"

# Types de points d'arrêt GDB : 2 = écriture, 3 = lecture, 4 = accès (Cemu : un seul à la fois)
WATCH_KINDS = {"write": 2, "read": 3, "access": 4}

# Arrêt à distance : créer ce fichier arrête proprement l'outil (le stub de Cemu
# gère mal une déconnexion brutale et reste bloqué sur l'ancienne connexion).
STOP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".probe_state", "gdb_stop")


class GdbClient:
    def __init__(self, host, port, timeout=None):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(timeout)
        self.buffer = b""

    # --- Couche paquets ------------------------------------------------------

    def _recv_byte(self):
        while not self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("Connexion fermée par Cemu")
            self.buffer += chunk
        byte, self.buffer = self.buffer[:1], self.buffer[1:]
        return byte

    def send_packet(self, payload):
        data = payload.encode("ascii")
        checksum = sum(data) & 0xFF
        frame = b"$" + data + b"#" + f"{checksum:02x}".encode("ascii")
        for _ in range(3):
            self.sock.sendall(frame)
            ack = self._recv_byte()
            if ack == b"+":
                return
            if ack == b"-":
                continue
            # Pas d'acquittement : on remet l'octet dans le tampon (mode sans ACK)
            self.buffer = ack + self.buffer
            return
        raise ConnectionError(f"Paquet refusé : {payload}")

    def recv_packet(self):
        while self._recv_byte() != b"$":
            pass
        payload = b""
        while True:
            byte = self._recv_byte()
            if byte == b"#":
                break
            payload += byte
        self._recv_byte()
        self._recv_byte()  # somme de contrôle (non vérifiée : liaison locale)
        self.sock.sendall(b"+")
        return payload.decode("ascii", errors="replace")

    def command(self, payload):
        self.send_packet(payload)
        return self.recv_packet()

    def interrupt(self):
        self.sock.sendall(b"\x03")

    def wait_packet(self, should_stop, poll=0.5):
        """Attend un paquet ; renvoie None si should_stop() devient vrai entre-temps."""
        while True:
            if self.buffer:
                return self.recv_packet()
            readable, _, _ = select.select([self.sock], [], [], poll)
            if readable:
                return self.recv_packet()
            if should_stop():
                return None

    # --- Commandes de haut niveau ----------------------------------------

    def read_register(self, number):
        reply = self.command(f"p{number:x}")
        if not reply or reply.startswith("E"):
            return None
        return int(reply[:8], 16)

    def read_pc_lr(self):
        pc = self.read_register(REG_PC)
        lr = self.read_register(REG_LR)
        if pc is None:
            # Repli : paquet « g » = 32 GPR (8 hex) + 32 FPR (16 hex) + pc, msr, cr, lr…
            regs = self.command("g")
            offset = 32 * 8 + 32 * 16
            if len(regs) >= offset + 8:
                pc = int(regs[offset:offset + 8], 16)
            if len(regs) >= offset + 32:
                lr = int(regs[offset + 24:offset + 32], 16)
        return pc, lr

    def read_memory(self, address, length):
        reply = self.command(f"m{address:x},{length:x}")
        if reply.startswith("E") or not reply:
            return None
        return bytes.fromhex(reply)


def parse_watch(text):
    address, _, length = text.partition(":")
    return int(address, 0), int(length or "4", 0)


def describe(value_bytes):
    if value_bytes is None:
        return "?"
    if len(value_bytes) == 4:
        as_int = struct.unpack(">I", value_bytes)[0]
        as_float = struct.unpack(">f", value_bytes)[0]
        return f"0x{as_int:08X} (u32 {as_int}, f32 {as_float:g})"
    return value_bytes.hex(" ").upper()


def main():
    parser = argparse.ArgumentParser(description="Journalise les écritures du jeu sur des adresses (stub GDB de Cemu).")
    parser.add_argument("watches", nargs="+", help="Adresses Wii U à surveiller, format ADRESSE[:TAILLE]")
    parser.add_argument("--kind", choices=WATCH_KINDS, default="write")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--log", help="Fichier où recopier le journal")
    args = parser.parse_args()

    log_file = open(args.log, "a", encoding="utf-8") if args.log else None

    def log(line):
        stamped = f"[{time.strftime('%H:%M:%S')}] {line}"
        print(stamped, flush=True)
        if log_file:
            log_file.write(stamped + "\n")
            log_file.flush()

    watches = [parse_watch(text) for text in args.watches]
    client = GdbClient(args.host, args.port)
    log(f"Connecté à {args.host}:{args.port}")
    client.command("qSupported")
    log(f"État initial : {client.command('?')}")

    kind = WATCH_KINDS[args.kind]
    for address, length in watches:
        reply = client.command(f"Z{kind},{address:x},{length:x}")
        status = "OK" if reply == "OK" else f"refusé ({reply or 'non supporté'})"
        log(f"Surveillance {args.kind} 0x{address:08X} ({length} octets) : {status}")

    previous = {address: client.read_memory(address, length) for address, length in watches}
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    log(f"Jeu relancé. Ctrl+C ou création de {STOP_FILE} pour arrêter.")
    client.send_packet(CONTINUE_ALL)

    stop_requested = False

    def should_stop():
        return os.path.exists(STOP_FILE)

    try:
        while True:
            reply = client.wait_packet(should_stop)
            if reply is None:
                stop_requested = True
                break
            if reply.startswith(("W", "X")):
                log(f"Le jeu s'est terminé : {reply}")
                break
            pc, lr = client.read_pc_lr()
            hit = re.search(r"(?:watch|rwatch|awatch):([0-9a-fA-F]+)", reply)
            hit_address = int(hit.group(1), 16) if hit else None
            changes = []
            for address, length in watches:
                current = client.read_memory(address, length)
                if current != previous[address] or address == hit_address:
                    changes.append(f"0x{address:08X} : {describe(previous[address])} -> {describe(current)}")
                previous[address] = current
            pc_text = f"0x{pc:08X}" if pc is not None else "?"
            lr_text = f"0x{lr:08X}" if lr is not None else "?"
            log(f"ARRÊT ({reply[:40]}) PC={pc_text} LR={lr_text} | " + (" ; ".join(changes) or "aucun changement visible"))
            client.send_packet(CONTINUE_ALL)
    except KeyboardInterrupt:
        stop_requested = True
    finally:
        if stop_requested:
            # Mise en pause, retrait des surveillances, puis on laisse le jeu tourner.
            log("Arrêt demandé : retrait des surveillances, le jeu continue.")
            try:
                client.interrupt()
                client.recv_packet()
                for address, length in watches:
                    client.command(f"z{kind},{address:x},{length:x}")
                client.send_packet(CONTINUE_ALL)
            except (ConnectionError, OSError) as error:
                log(f"Nettoyage incomplet : {error}")
            if os.path.exists(STOP_FILE):
                os.remove(STOP_FILE)
        if log_file:
            log_file.close()


if __name__ == "__main__":
    main()
