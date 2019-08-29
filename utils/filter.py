from typing import List


class Filter:

    def __call__(self, f_type="npc", **kwargs):
        if f_type == "npc":
            return self.__filter_npc_ids()
        elif f_type == "quest":
            return self.__filter_quest_ids()

    @staticmethod
    def __filter_quest_ids() -> List[int]:
        quest_id_list = []
        with open("data/questDB.lua", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("["):
                    quest_id = line[1:line.index("]")]
                    quest_id_list.append(int(quest_id))
        return quest_id_list

    @staticmethod
    def __filter_npc_ids() -> List[int]:
        npc_id_list = []
        with open("data/spawnDB.lua", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("["):
                    npc_id = line[1:line.index("]")]
                    npc_id_list.append(int(npc_id))
        return npc_id_list


if __name__ == '__main__':
    f = Filter()
    npc_ids = f("npc")
    print(npc_ids)

    quest_ids = f("quest")
    print(quest_ids)
