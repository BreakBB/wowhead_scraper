import json
from pathlib import Path

from utils.paths import OUTPUT_DIR


class Formatter:

    lang: str
    lang_dir: Path

    def __call__(self, lang="en", f_type="npc", **kwargs):
        self.lang = lang
        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            self.lang_dir.mkdir()

        if f_type == "npc":
            self.__format_npc_names()
        elif f_type == "quest":
            self.__format_quests()

    def __format_npc_names(self):
        with Path(self.lang_dir / "npc_data.json").open("r", encoding="utf-8") as f:
            npc_input = json.load(f)
            npc_input.sort(key=lambda k: int(k["id"]))
        with Path(self.lang_dir / "lookup.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name()
            g.write(table_name)

            for item in npc_input:
                name = item["name"]
                name = name.replace("'", "\\'")
                g.write("[{}] = '{}',\n".format(item["id"], name))

            g.write("}")

    def __format_quests(self):
        with Path(self.lang_dir / "quest_data.json").open("r", encoding="utf-8") as f:
            quest_input = json.load(f)
            quest_input.sort(key=lambda k: k["id"])
        with Path(self.lang_dir / "lookup.lua").open("a", encoding="utf-8") as g:
            table_name = self.__get_table_name("quest")
            g.write(table_name)

            for item in quest_input:
                title = self.__get_title(item)
                objective = self.__get_objective(item)
                description = self.__get_description(item)

                g.write("[{id}] = {{{title}, {desc}, {obj}}},\n".format(id=item["id"], title=title,
                                                                        desc=description, obj=objective))

            g.write("}")

    def __get_table_name(self, target="npc"):
        lang = self.lang
        if target == "npc":
            table_name = "LangNameLookup['{}'] = {{\n"
        else:
            table_name = "\nLangQuestLookup['{}'] = {{\n"
        if lang == "en":
            return table_name.format("enUS")
        elif lang == "de":
            return table_name.format("deDE")
        elif lang == "fr":
            return table_name.format("frFR")
        elif lang == "es":
            return table_name.format("esES")
        elif lang == "ru":
            return table_name.format("ruRU")
        elif lang == "cn":
            return table_name.format("zhCN")
        elif lang == "pt":
            return table_name.format("ptBR")
        else:
            raise ValueError("Language '{}' not supported for formatting!".format(lang))

    @staticmethod
    def __get_objective(item):
        objective = item["objective"]
        objective = objective.replace("'", "\\'")
        if objective:
            objective = "'" + objective + "'"
        else:
            objective = "nil"
        return objective

    @staticmethod
    def __get_title(item):
        title = item["title"]
        title = title.replace("'", "\\'")
        if title:
            title = "'" + title + "'"
        else:
            title = "nil"
        return title

    @staticmethod
    def __get_description(item):
        description = item["description"]
        description = description.replace("'", "\\'")
        if description:
            description = "'" + description + "'"
        else:
            description = "nil"
        return description


if __name__ == '__main__':
    f = Formatter()
    f("pt", "npc")
    f("pt", "quest")
