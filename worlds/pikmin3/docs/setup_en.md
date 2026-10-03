# Pikmin 3 (Cemu) Setup Guide

## Required software

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.7 or newer
- [Cemu](https://cemu.info/) 2.6 or newer, on **Windows**
- **Pikmin 3 (Europe)**, version 1 (disc version, **no update installed**), dumped from your own Wii U
- The `pikmin3.apworld` file

Other versions (USA, Japan, update 2.0.0, Pikmin 3 Deluxe) are not supported yet: the game code is patched at fixed
addresses that only match the European v1 executable.

## Installation

1. Double-click `pikmin3.apworld` (or use *Install APWorld* in the Archipelago Launcher).
2. Open the **Pikmin 3 Client** from the Archipelago Launcher and type `/install_pack`.
   This copies the *Archipelago* graphic pack into `%APPDATA%\Cemu\graphicPacks\Pikmin3_Archipelago`.
   If your Cemu data folder is elsewhere, give it as an argument: `/install_pack D:\Cemu`.
3. In Cemu: right-click Pikmin 3 > *Edit graphic packs*, then enable **Pikmin 3 > Mods > Archipelago**.
   Disable any other mod that changes the Pikmin limit or the fruit juice.
4. **Back up your save** (`mlc01\usr\save\00050000\1012be00`) before your first Archipelago session.

The graphic pack does nothing on its own: without the client, the game behaves normally.

## Create your options file

Use the [player options page](../player-options) to create your YAML file, or generate a template from the Launcher
(*Generate Template Options*).

## Playing

1. Start Pikmin 3 in Cemu and load your **Story mode** save (Mission and Bingo modes are ignored).
2. Start the Pikmin 3 Client and connect to the server (`/connect address:port`, then your slot name).
3. The client finds Cemu by itself. `/cemu` shows the connection state, `/state` shows what the client reads.

### What changes in game

- Juicing a fruit sends a check but **gives no juice**. Juice comes from the fruit items you receive.
- With *Progressive Pikmin Limit*, the field limit starts low and rises with each "Progressive Pikmin Limit" item.
- *Juice mode* protects you from running out of juice: `safe` keeps at least 2 bottles, `no_consumption` gives back
  the bottle your crew drinks every night, `normal` changes nothing (you can lose the game).
- Default goal: defeat the final boss in Formidable Oak **and** juice the requested number of fruits.
- With *Progressive Zones*, you start with Tropical Wilds and Garden of Hope; each "Progressive Zone" item opens the
  next area (Distant Tundra, Twilight River, Formidable Oak). The client closes an area the story would open too early.
- With *Progressive Pikmin* (off by default), four items unlock Rock, Yellow, Winged and Blue Pikmin, at the end of the
  day the item arrives.

### Reloading a day

Items given during a day are lost if you reload that day. The client detects when the game was restarted or when you
go back to an earlier day, and gives those items again. If you reloaded a day without restarting the game (for example
*Retry Day* from the pause menu), type `/resync_day` once you are back on the planet.

## Known limitations (version 1.0)

- Only the European v1 version is supported.
- Progressive areas and Progressive Pikmin (experimental): not tried in a real game with the client yet.
- "Final boss" goal: the boss can only be fought once the story is far enough (after Louie is rescued).
- The "check ↔ area" logic is derived from a real playthrough (conservative, not exact yet).
- No death link and no Mission mode checks yet.
