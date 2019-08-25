# Questie Scraper

This project targets to scrape the [WowHead](https://classic.wowhead.com) website and extract information about NPCs and quests. These information are used for localization of the [Questie Addon](https://github.com/AeroScripts/QuestieDev/).

## How to use

### Install requirements

You will need Python to run any part of this project and the modules can be installed using the `requirements.txt`:

`pip install -r requirements.txt`

### Running the scraper

Currently this project can only be used via command line:

`python runner.py`

The available parameters are:

| Parameter        | Type  | Description                                                 | Default |
|------------------|-------|-------------------------------------------------------------|---------|
| `-l`, `--lang`   | `str` | The language you want to scrape. Either `en`, `de` or `fr`. | `en`    |
| `-t`, `--target` | `str` | The target you want to scrape. Either 'npc' or 'quest'.     | `npc`   |