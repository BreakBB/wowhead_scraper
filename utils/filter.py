from pathlib import Path
from typing import List, Union
from utils.paths import IDS_DIR


class Filter:

    ids = []

    def __call__(self, f_type="npc", **kwargs):
        if f_type == "item":
            return self.__filter_ids("itemDB.lua")
        elif f_type == "npc":
            return self.__filter_ids("spawnDB.lua")
        elif f_type == "object":
            return self.__filter_ids("objectDB.lua")
        elif f_type == "quest":
            return self.__filter_ids("questDB.lua")

    def __filter_ids(self, target_file: str) -> Union[List[int], None]:
        path = Path(IDS_DIR / target_file)
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("["):
                    i = line[1:line.index("]")]
                    self.ids.append(int(i))
        return self.ids

    def write_to_file(self, table_name: str, target_file: str):
        with open(IDS_DIR / target_file, "w", encoding="utf-8") as f:
            f.write(table_name + " = [\n")
            for nid in self.ids:
                f.write("  {},\n".format(nid))
            f.write("]\n")
        pass


if __name__ == '__main__':
    fil = Filter()

    item_ids = fil("item")
    if not item_ids:
        print("itemDB not found")
    else:
        fil.write_to_file("ITEM_IDS", "itemIDs.py")
    #
    # npc_ids = fil("npc")
    # if not npc_ids:
    #     print("npcDB not found")
    # else:
    #     fil.write_to_file("NPC_IDS", "npcIDs.py")
    #
    # object_ids = fil("object")
    # if not object_ids:
    #     print("objectDB not found")
    # else:
    #     fil.write_to_file("OBJECT_IDS", "objectIDs.py")
    #
    # quest_ids = fil("quest")
    # if not quest_ids:
    #     print("questDB not found")
    # else:
    #     fil.write_to_file("QUEST_IDS", "questIDs.py")
