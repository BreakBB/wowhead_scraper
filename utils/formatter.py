import json
from pathlib import Path


class Formatter:

    def __call__(self, lang="en", f_type="npc", **kwargs):

        if f_type == "npc":
            self.__format_npc_names(lang)
        elif f_type == "quest":
            with open(Path(__file__).parent / "../output/{}_quest_data.json".format(lang), "r", encoding="utf-8") as f:
                quest_input = json.load(f)
                quest_input.sort(key=lambda k: k["id"])

            with open(Path(__file__).parent / "../output/{}.lua".format(lang), "a", encoding="utf-8") as g:
                table_name = self.__get_table_name(lang, "quest")
                g.write(table_name)

                for item in quest_input:
                    title = self.__get_title(item)
                    objective = self.__get_objective(item)
                    description = self.__get_description(item)

                    g.write("[{id}] = {{{title}, {desc}, {obj}}},\n".format(id=item["id"], title=title,
                                                                            desc=description, obj=objective))

                g.write("}")

    def __get_table_name(self, lang, target="npc"):
        if target == "npc":
            table_name = "LangNameLookup['{}'] = {{\n"
        else:
            table_name = "\nLangQuestLookup['{}'] = {{\n"
        if lang == "en":
            table_name = table_name.format("enUS")
        if lang == "de":
            table_name = table_name.format("deDE")
        if lang == "fr":
            table_name = table_name.format("frFR")
        if lang == "es":
            table_name = table_name.format("esES")
        if lang == "ru":
            table_name = table_name.format("ruRU")
        if lang == "ch":
            table_name = table_name.format("zhCN")
        return table_name

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

    def __format_npc_names(self, lang):
        with open(Path(__file__).parent / "../output/{}_npc_data.json".format(lang), "r", encoding="utf-8") as f:
            npc_input = json.load(f)
            npc_input.sort(key=lambda k: int(k["id"]))
        with open(Path(__file__).parent / "../output/{}.lua".format(lang), "w", encoding="utf-8") as g:
            table_name = self.__get_table_name(lang)
            g.write(table_name)

            for item in npc_input:
                name = item["name"]
                name = name.replace("'", "\\'")
                g.write("[{}] = '{}',\n".format(item["id"], name))

            g.write("}")


if __name__ == '__main__':
    f = Formatter()
    f("es", "npc")
    f("es", "quest")
