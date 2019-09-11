from pathlib import Path
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
        with open(Path(__file__).parent.parent / "data/questDB.lua", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("["):
                    quest_id = line[1:line.index("]")]
                    quest_id_list.append(int(quest_id))
        return quest_id_list

    @staticmethod
    def __filter_npc_ids() -> List[int]:
        npc_id_list = []
        with open(Path(__file__).parent.parent / "data/spawnDB.lua", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("["):
                    npc_id = line[1:line.index("]")]
                    npc_id_list.append(int(npc_id))
        return npc_id_list


if __name__ == '__main__':
    fil = Filter()
    npc_ids = fil("npc")
    with open(Path(__file__).parent.parent / "data/npcIDs.py", "w", encoding="utf-8") as f:
        f.write("NPC_IDS = [\n")
        for qid in npc_ids:
            f.write("  {},\n".format(qid))
        f.write("]\n")

    quest_ids = fil("quest")
    with open(Path(__file__).parent.parent / "data/questIDs.py", "w", encoding="utf-8") as f:
        f.write("QUEST_IDS = [\n")
        for qid in quest_ids:
            f.write("  {},\n".format(qid))
        f.write("]\n")
