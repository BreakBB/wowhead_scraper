# Wowhead Scraper

This project targets to scrape the [Wowhead](https://classic.wowhead.com) website and extract information about NPCs, quests, items, objects and experience points (XP). These information are primarily used for localization of the [Questie Addon](https://github.com/AeroScripts/QuestieDev/).

## How to use

### Install requirements

You will need Python to run any part of this project and the modules can be installed using the `requirements.txt`:

`pip install -r requirements.txt`

### Running the scraper

Currently this project can only be used via command line:

`python runner.py`

The available parameters are:

| Parameter         | Type  | Description                          | Possible values                                | Default |
|-------------------|-------|--------------------------------------|------------------------------------------------|---------|
| `-l`, `--lang`    | `str` | The language you want to scrape.     | `en`, `de`, `fr`, `es`, `ru`, `cn`, `pt`, `ko` | `en`    |
| `-t`, `--target`  | `str` | The target you want to scrape.       | `npc`, `quest`, `item`, `object`, `xp`         | `npc`   |
| `-v`, `--version` | `str` | The game version you want to scrape. | `classic`, `tbc`, `wotlk`                      | `wotlk` |
