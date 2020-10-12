import json
from pathlib import Path
from typing import TextIO, List

from utils.paths import OUTPUT_DIR


class Formatter:
    lang: str
    lang_dir: Path

    def __call__(self, lang="en", f_type="npc", **kwargs):
        print("Starting Formatter...")
        self.lang = lang
        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            print("Directory for language '{}' doesn't exist. Creating it...".format(self.lang))
            self.lang_dir.mkdir()

        if f_type == "item":
            self.__format_item_names()
        elif f_type == "npc":
            self.__format_npc_names()
        elif f_type == "object":
            self.__format_object_names()
        elif f_type == "quest":
            self.__format_quests()
        elif f_type == "xp":
            self.__format_quests_xp()

        print("Formatting done!")

    def __format_item_names(self):
        item_input = self.__load_json_file("item_data.json")
        with Path(self.lang_dir / "lookupItems.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("item")
            self.__write_id_to_string_table(g, item_input, table_name)

    def __format_npc_names(self):
        npc_input = self.__load_json_file("npc_data.json")
        with Path(self.lang_dir / "lookupNpcs.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name()
            g.write(table_name)
            for item in npc_input:
                name = self.__filter_text(item["name"])
                subname = self.__filter_text(item["subname"])
                g.write("[{}] = {{{},{}}},\n".format(item["id"], name, subname))
            g.write("}\n")

    def __write_id_to_string_table(self, g, data, table_name):
        g.write(table_name)
        for item in data:
            name = self.__filter_text(item["name"])
            g.write("[{}] = {},\n".format(item["id"], name))
        g.write("}\n")

    def __format_object_names(self):
        object_input = self.__load_json_file("object_data.json")
        with Path(self.lang_dir / "lookupObjects.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("object")
            g.write(table_name)

            for item in object_input:
                name = self.__filter_text(item["name"])
                g.write("[{}] = {},\n".format(item["id"], name))

            g.write("}\n")

    def __load_json_file(self, file_name: str):
        print("Loading '{}'...".format(file_name))
        with Path(self.lang_dir / file_name).open("r", encoding="utf-8") as f:
            data = json.load(f)
            data.sort(key=lambda k: int(k["id"]))
        print("Data contains {} entries".format(len(data)))
        return data

    def __format_quests(self) -> None:
        quest_input = self.__load_json_file("quest_data.json")
        with Path(self.lang_dir / "lookupQuests.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("quest")
            g.write(table_name)

            for item in quest_input:
                title = self.__filter_text(item["title"])
                objective = self.__filter_list(item["objective"])
                description = self.__filter_list(item["description"])

                g.write("[{id}] = {{{title},".format(id=item["id"], title=title))
                self.__write_list(description, g)
                g.write(",")
                self.__write_list(objective, g)
                g.write("},\n")
            g.write("}\n")

    def __format_quests_xp(self) -> None:
        with Path(self.lang_dir / "quest_xp_data.json").open("r", encoding="utf-8") as f:
            quest_xp_input = json.load(f)
            quest_xp_input.sort(key=lambda k: k["id"])
        with Path(self.lang_dir / "lookupQuestXp.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("xp")
            g.write(table_name)

            for item in quest_xp_input:
                quest_id = item["id"]
                quest_xp = item["xp"]
                g.write("[{id}] = {xp},\n".format(id=quest_id, xp=quest_xp))

            g.write("}\n")

    def __get_table_name(self, target: str = "npc") -> str:
        lang = self.lang
        table_name = ""
        if target == "item":
            table_name = "LangItemLookup[\"{}\"] = {{\n"
        elif target == "npc":
            table_name = "LangNameLookup[\"{}\"] = {{\n"
        elif target == "object":
            table_name = "LangObjectLookup[\"{}\"] = {{\n"
        elif target == "quest":
            table_name = "LangQuestLookup[\"{}\"] = {{\n"
        elif target == 'xp':
            table_name = "LangQuestXpLookup[\"{}\"] = {{\n"

        if lang == "en":
            return table_name.format("enUS")
        elif lang == "de":
            return table_name.format("deDE")
        elif lang == "fr":
            return table_name.format("frFR")
        elif lang == "es":
            return table_name.format("esES")
        elif lang == "mx":
            return table_name.format("esMX")
        elif lang == "ru":
            return table_name.format("ruRU")
        elif lang == "cn":
            return table_name.format("zhCN")
        elif lang == "pt":
            return table_name.format("ptBR")
        elif lang == "ko":
            return table_name.format("koKR")
        else:
            raise ValueError("Language '{}' not supported for formatting!".format(lang))

    def __filter_text(self, text: str) -> str:
        text = text.replace("\\", "")
        text = text.replace("\"", "\\\"")
        if self.lang == "ru":
            text = text.replace("|3-6(<раса>)", "<раса>")
            text = text.replace("|3-1(<класс>)", "<класс>")
            text = text.replace("|3-2(<класс>)", "<класс>")
            text = text.replace("|3-6(<класс>)", "<класс>")

        if not text:
            return "nil"
        return "\"" + text + "\""

    def __filter_list(self, text_list: List[str]) -> List[str]:
        ret_list = []
        for text in text_list:
            ret_list.append(self.__filter_text(text))
        return ret_list

    @staticmethod
    def __write_list(sentences: List[str], g: TextIO) -> None:
        if (not sentences) or (sentences[0] == "nil"):
            g.write(" nil")
            return

        g.write(" {")
        for i, s in enumerate(sentences):
            if i == (len(sentences) - 1):  # The last sentence should be added without ","
                g.write("{desc}".format(desc=s))
            else:
                g.write("{desc},".format(desc=s))
        g.write("}")
