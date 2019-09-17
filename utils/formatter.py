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
        if f_type == "object":
            self.__format_object_names()
        elif f_type == "quest":
            self.__format_quests()

    def __format_npc_names(self):
        with Path(self.lang_dir / "npc_data.json").open("r", encoding="utf-8") as f:
            npc_input = json.load(f)
            npc_input.sort(key=lambda k: int(k["id"]))
        with Path(self.lang_dir / "lookupNpcs.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name()
            g.write(table_name)

            for item in npc_input:
                name = item["name"]
                name = name.replace("'", "\\'")
                name = name.replace("\"", "\\\"")
                g.write("[{}] = \"{}\",\n".format(item["id"], name))

            g.write("}\n")

    def __format_object_names(self):
        with Path(self.lang_dir / "object_data.json").open("r", encoding="utf-8") as f:
            npc_input = json.load(f)
            npc_input.sort(key=lambda k: int(k["id"]))
        with Path(self.lang_dir / "lookupObjects.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("object")
            g.write(table_name)

            for item in npc_input:
                name = item["name"]
                if name.startswith("["):
                    continue
                name = name.replace("'", "\\'")
                name = name.replace("\"", "\\\"")
                g.write("[\"{}\"] = {},\n".format(name, item["id"]))

            g.write("}\n")

    def __format_quests(self):
        with Path(self.lang_dir / "quest_data.json").open("r", encoding="utf-8") as f:
            quest_input = json.load(f)
            quest_input.sort(key=lambda k: k["id"])
        with Path(self.lang_dir / "lookupQuests.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("quest")
            g.write(table_name)

            for item in quest_input:
                title = self.__filter_text(item["title"])
                objective = self.__filter_text(item["objective"])
                description = self.__filter_text(item["description"])

                g.write("[{id}] = {{{title}, {desc}, {obj}}},\n".format(id=item["id"], title=title,
                                                                        desc=description, obj=objective))

            g.write("}\n")

    def __get_table_name(self, target="npc"):
        lang = self.lang
        if target == "npc":
            table_name = "LangNameLookup['{}'] = {{\n"
        elif target == "object":
            table_name = "\nLangObjectLookup['{}'] = {{\n"
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
    def __filter_text(text):
        text = text.replace("\\", "")
        text = text.replace("'", "\\'")
        text = text.replace("\"", "\\\"")
        if text:
            text = "'" + text + "'"
        else:
            text = "nil"
        return text


if __name__ == '__main__':
    f = Formatter()
    f("cn", "object")
    # f("pt", "quest")
