import re

QUEST = "Quest"

FILTERS = [
    "A level ",
    "A Quest",
    "A quest.",
    "A quest from Classic",
    "A Children's Week quest",
    "A Darkmoon Faire quest",
    "A Hallow's End quest",
    "A Lunar Festival quest",
    "A Midsummer quest",
    "A Westfall Quest",
    "A Winter Veil quest.",
    "Completing this quest will",
    "If you are interested in the 8.1.5",
    "You will learn",
    "You will receive",
    "The following spell will be cast on you",
    "You will be able to choose one of these rewards",
    "Upon completion of this quest you will gain",
    "Temp text 02 - log."
]

REGEX = [
    r"See .* quest.",
    r"See current version of this quest here: .*\."
]

if __name__ == '__main__':
    text = "See current version of this quest here: Villains of Darrowshire. "
    matches = re.sub(r"See current version of this quest here: .*\. ", "", text)
    print(matches)
