import json
from pathlib import Path
from typing import TextIO, List

from utils.paths import OUTPUT_DIR


class Formatter:
    lang: str
    target_dir: Path

    def __call__(self, lang="en", f_type="npc", **kwargs):
        print("Starting Formatter...")
        self.lang = lang
        self.target_dir = OUTPUT_DIR / f_type
        if not self.target_dir.exists():
            print("Directory '{}' doesn't exist. Creating it...".format(self.target_dir))
            self.target_dir.mkdir()

        if f_type == "item":
            self.__format_item_names(lang)
        elif f_type == "npc":
            self.__format_npc_names(lang)
        elif f_type == "object":
            self.__format_object_names(lang)
        elif f_type == "quest":
            self.__format_quests(lang)
        elif f_type == "xp":
            self.__format_quests_xp(lang)

        print("Formatting done!")

    def __format_item_names(self, lang):
        item_input = self.__load_json_file(lang + "_data.json")
        lang = self.__get_lang_code()
        with Path(self.target_dir / (lang + ".lua")).open("w", encoding="utf-8") as g:
            self.__write_lua_file_header(g)
            table_name = self.__get_table_name("item")
            self.__write_id_to_string_table(g, item_input, table_name)

    def __format_npc_names(self, lang):
        npc_input = self.__load_json_file(lang + "_data.json")
        lang = self.__get_lang_code()
        with Path(self.target_dir / (lang + ".lua")).open("w", encoding="utf-8") as g:
            self.__write_lua_file_header(g)
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

    def __format_object_names(self, lang):
        object_input = self.__load_json_file(lang + "_data.json")
        lang = self.__get_lang_code()
        with Path(self.target_dir / (lang + ".lua")).open("w", encoding="utf-8") as g:
            self.__write_lua_file_header(g)
            table_name = self.__get_table_name("object")
            g.write(table_name)

            for item in object_input:
                name = self.__filter_text(item["name"])
                g.write("[{}] = {},\n".format(item["id"], name))

            g.write("}\n")

    def __load_json_file(self, file_name: str):
        print("Loading '{}'...".format(file_name))
        with Path(self.target_dir / file_name).open("r", encoding="utf-8") as f:
            data = json.load(f)
            data.sort(key=lambda k: int(k["id"]))
        print("Data contains {} entries".format(len(data)))
        return data

    def __format_quests(self, lang) -> None:
        quest_input = self.__load_json_file(lang + "_data.json")
        lang = self.__get_lang_code()
        with Path(self.target_dir / (lang + ".lua")).open("w", encoding="utf-8") as g:
            self.__write_lua_file_header(g)
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

    def __write_lua_file_header(self, g: TextIO) -> None:
        g.write('if GetLocale() ~= "{}" then\n'.format(self.__get_lang_code()))
        g.write('    return\n')
        g.write('end\n\n')
        g.write('---@type l10n\n')
        g.write('local l10n = QuestieLoader:ImportModule("l10n")\n\n')

    def __format_quests_xp(self, lang) -> None:
        with Path(self.target_dir / lang + "_xp_data.json").open("r", encoding="utf-8") as f:
            quest_xp_input = json.load(f)
            quest_xp_input.sort(key=lambda k: k["id"])
        lang = self.__get_lang_code()
        with Path(self.target_dir / (lang + ".lua")).open("w", encoding="utf-8") as g:
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
            table_name = "l10n.itemLookup[\"{}\"] = {{\n"
        elif target == "npc":
            table_name = "l10n.npcNameLookup[\"{}\"] = {{\n"
        elif target == "object":
            table_name = "l10n.objectLookup[\"{}\"] = {{\n"
        elif target == "quest":
            table_name = "l10n.questLookup[\"{}\"] = {{\n"
        elif target == 'xp':
            table_name = "l10n.xpLookup[\"{}\"] = {{\n"

        return table_name.format(self.__get_lang_code())

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

    def __get_lang_code(self) -> str:
        if self.lang == "en":
            return "enUS"
        elif self.lang == "de":
            return "deDE"
        elif self.lang == "fr":
            return "frFR"
        elif self.lang == "es":
            return "esES"
        elif self.lang == "mx":
            return "esMX"
        elif self.lang == "ru":
            return "ruRU"
        elif self.lang == "cn":
            return "zhCN"
        elif self.lang == "pt":
            return "ptBR"
        elif self.lang == "ko":
            return "koKR"
        else:
            raise ValueError("Language '{}' not supported for formatting!".format(self.lang))


if __name__ == '__main__':
    f = Formatter()
    f("de", "quest")