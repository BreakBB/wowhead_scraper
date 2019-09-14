from pathlib import Path

from utils.paths import OUTPUT_DIR


class Merger:
    lang: str
    lang_dir: Path

    def __init__(self, lang="en"):
        self.lang = lang

        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            self.lang_dir.mkdir()

    def __call__(self):
        new_file, old_file, temp_file = self.__get_files()

        self.__copy_lines(new_file, old_file, temp_file)
        self.__rename_files(new_file, old_file, temp_file)

    def __get_files(self):
        old_file = self.lang_dir / "lookup_old.lua"
        if not old_file.exists():
            raise ValueError("Could not find old lookup file '{}'".format(old_file))
        new_file = self.lang_dir / "lookup.lua"
        if not new_file.exists():
            raise ValueError("Could not find new lookup file '{}'".format(new_file))
        temp_file = self.lang_dir / "lookup_temp.lua"
        return new_file, old_file, temp_file

    @staticmethod
    def __copy_lines(new_file, old_file, temp_file):
        with old_file.open("r", encoding="utf-8") as old, \
                new_file.open("r", encoding="utf-8") as new, \
                temp_file.open("w", encoding="utf-8") as tmp:

            for old_line, new_line in zip(old, new):
                if len(old_line) > len(new_line):
                    tmp.write(old_line)
                else:
                    tmp.write(new_line)

    def __rename_files(self, new_file: Path, old_file: Path, temp_file: Path):
        old_file.unlink()
        new_file.rename(self.lang_dir / "lookup_old.lua")
        lookup_path = Path(self.lang_dir / "lookup.lua")
        if lookup_path.exists():
            lookup_path.unlink()
        temp_file.rename(lookup_path)


if __name__ == '__main__':
    m = Merger("pt")
    m()
