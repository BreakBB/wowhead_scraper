from pathlib import Path

from utils.paths import OUTPUT_DIR
from shutil import copyfile


class Merger:
    lang: str
    target: str
    lang_dir: Path

    def __init__(self, lang="en", target="Npcs"):
        self.lang = lang
        self.target = target

        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            self.lang_dir.mkdir()

    def __call__(self):
        print("Starting Merger...")
        new_file, old_file, temp_file = self.__get_files()

        self.__copy_lines(new_file, old_file, temp_file)
        self.__rename_files(new_file, old_file, temp_file)
        print("Merging done!")

    def __get_files(self):
        old_file = self.lang_dir / "lookup{}_old.lua".format(self.target)
        if not old_file.exists():
            raise ValueError("Could not find old lookup file '{}'".format(old_file))
        new_file = self.lang_dir / "lookup{}.lua".format(self.target)
        if not new_file.exists():
            raise ValueError("Could not find new lookup file '{}'".format(new_file))
        temp_file = self.lang_dir / "lookup{}_temp.lua".format(self.target)
        return new_file, old_file, temp_file

    def __copy_lines(self, new_file, old_file, temp_file):
        with old_file.open("r", encoding="utf-8") as old:
            old_lines = old.readlines()
        with new_file.open("r", encoding="utf-8") as new:
            new_lines = new.readlines()

        if len(old_lines) != len(new_lines):
            raise ValueError("Old ({}) and new ({}) lines doesn't match".format(len(old_lines), len(new_lines)))

        with temp_file.open("w", encoding="utf-8") as tmp:
            old_counter = 0
            new_counter = 0
            for old_line, new_line in zip(old_lines, new_lines):
                if len(old_line) > len(new_line):
                    self.__write_splits(old_line, tmp)
                    old_counter += 1
                else:
                    self.__write_splits(new_line, tmp)
                    new_counter += 1
            print("Wrote {} old and {} new lines".format(old_counter, new_counter))

    @staticmethod
    def __write_splits(line, tmp):
        splits = line.split("\", \"")
        if len(splits) > 2:
            tmp.write(splits[0] + "\", ")
            tmp.write("{\"" + splits[1] + "\"}, ")
            tmp.write("{\"" + splits[2][:-2] + "},\n")
        else:
            tmp.write(line)

    def __rename_files(self, new_file: Path, old_file: Path, temp_file: Path):
        while old_file.exists():
            old_file.unlink()
        previous_path = self.lang_dir / "lookup{}_previous.lua".format(self.target)
        while previous_path.exists():
            previous_path.unlink()
        new_file.rename(previous_path)
        lookup_path = Path(self.lang_dir / "lookup{}.lua".format(self.target))
        while lookup_path.exists():
            lookup_path.unlink()
        temp_file.rename(lookup_path)
        copyfile(str(lookup_path), self.lang_dir / "lookup{}_old.lua".format(self.target))


if __name__ == '__main__':
    m = Merger("de", "Quests")
    m()

# Useful RegEx to find non escaped backslashes
# (?<!(\\|{|(", )|\[))"(?!(, ({|"|nil)|}|\]))
