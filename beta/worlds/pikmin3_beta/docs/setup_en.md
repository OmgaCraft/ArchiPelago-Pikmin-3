# Pikmin 3 Beta (Cemu) Setup Guide

## Required software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.7 or newer
- [Cemu](https://cemu.info/) 2.6 or newer, on **Windows**
- **Pikmin 3 (Europe)**, version 1 (disc version, **no update installed**), dumped from your own Wii U
- The `pikmin3_beta.apworld` file

## Installation

1. Double-click `pikmin3_beta.apworld` (or use *Install APWorld* in the Archipelago Launcher).
   It can stay installed next to the final `pikmin3.apworld`: they are two different games.
2. Open the **Pikmin 3 Beta Client** from the Archipelago Launcher and type `/install_pack`.
3. In Cemu: right-click Pikmin 3 > *Edit graphic packs*, enable **Pikmin 3 > Mods > Archipelago Beta** and
   **disable Pikmin 3 > Mods > Archipelago** (both patch the same game code).
4. **Back up your save** (`mlc01\usr\save\00050000\1012be00`).

## Playing

1. Start Pikmin 3 in Cemu and load your **Story mode** save.
2. Start the Pikmin 3 Beta Client and connect to the server.
3. Commands: `/cemu`, `/state`, `/resync_day`, and for the beta `/note <text>` (describe what you just did) and
   `/decouvertes` (last memory changes). The discovery journal also works without a server connection.

The full journal is written to `Archipelago\logs\Pikmin3Beta_decouvertes.txt`.
