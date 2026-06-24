
def generateDesignator(acronym, suffix, modifier=""):
    if modifier == "":
        return acronym + " " + suffix
    else:
        return acronym + " " + suffix + "-" + modifier