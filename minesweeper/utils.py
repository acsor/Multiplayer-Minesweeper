

def is_boolean(x):
    choices = {"true": True, "false": False}

    if x not in choices.keys():
        raise ValueError("%s not in %s" % (x, choices.keys()))

    return choices[x]
