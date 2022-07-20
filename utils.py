
def convert(string):

    split = string.split(":")
    if len(split[0]) == 1:
        string = "0"+string

    if string[-2:] == "AM" and string[:2] == "12":
        return "00" + string[2:-2]

    elif string[-2:] == "AM":
        return string[:-2]

    elif string[-2:] == "PM" and string[:2] == "12":
        return string[:-2]
    
    else:
        return str(int(string[:2]) + 12) + string[2:5]
