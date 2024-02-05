

from time import monotonic


def generateDesignator(acronym, suffix, modifier=""):
    if modifier == "":
        return acronym + " " + suffix + "-" + modifier
    else:
        return acronym + " " + suffix