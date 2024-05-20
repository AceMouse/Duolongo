import random 
import os
import sys

languages = {
        "F": "French",
        "E": "English",
        }

items = {
        "S":("Streak saver", 10),
        "R":("RAGE!", 50)
        }

def get_lang_mode_file_name(lang_code, mode):
    return f"{lang_code}_{mode}.txt"

def get_variable_file_name(variable):
    return f"{variable}.txt"

def get_list(file_name):
    if not os.path.isfile(file_name):
        return []
    with open(file_name, "r") as file:
        return file.read().strip().split("\n")

def get_variable(file_name, type, default):
    if not os.path.isfile(file_name):
        return default
    with open(file_name, "r") as file :
        try:
            return type(file.read())
        except:
            return default

def save_variable(file_name, value):
    with open(file_name, "w") as file:
        file.write(str(value))

def add_to_list(file_name, to_add):
    with open(file_name, "a") as file:
        file.write(f"{to_add}\n")

def play(langs, randomize, mode):
    sentances = dict()
    for lang_code in langs:
        file_name = get_lang_mode_file_name(lang_code, mode)
        sentances[lang_code] = get_list(file_name)
    streak_file_name = get_variable_file_name("streak")
    streak = get_variable(streak_file_name, int, default=0)
    points_file_name = get_variable_file_name("points")
    points = get_variable(points_file_name, int, default=streak)
    while True:
        streak_savers = get_from_inventory("S")
        if randomize:
            random.shuffle(langs)

        questions = sentances[langs[0]]
        answers   = sentances[langs[1]]
        if len(questions) == 0:
            print("There are no more questions left!")
            return streak 
        number = random.randint(0,len(questions)-1)

        question        = questions[number]
        expected_answer =   answers[number]

        answer_lang = languages[langs[1]]

        print(f"Points: {points}")
        print(f"Streak: {streak}")
        print(f"Translate \"{question}\" to {answer_lang}:")
        answer = input() 
        if answer.upper() == "B":
            return streak
        if answer.lower() != expected_answer.lower():
            print(f"Wrong! The expected answer is: \"{expected_answer}\"")
            if streak_savers > 0:
                add_to_inventory("S", -1)
            else:
                streak = 0
                save_variable(streak_file_name, streak)
            continue
        print("Correct!")
        for lang in langs:
            del sentances[lang][number]
        streak += 1 
        points += 1 
        save_variable(streak_file_name, streak)
        save_variable(points_file_name, points)
    return streak  

def lang_menu(languages, direction="from"):
    if len(languages) == 1:
        return list(languages)[0]
    lang_bindings = dict()
    for lang_code, lang_name in languages.items():
        lang_bindings[lang_code] = (f"To use the {lang_name} language",None)
    lang_bindings["B"] = ("To go back",None)

    return menu(f"Pick a language to translate {direction}", lang_bindings)

def play_menu():
    mode_bindings = {
            "W":("To play words",None),
            "S":("To play sentances",None),
            "B":("To go back",None)}
    modes = menu("Play menu", mode_bindings)
    if modes == "B":
        return 0
    lang1 = lang_menu(languages)
    if lang1 == "B":
        return 0
    lang_name1 = languages[lang1]
    del languages[lang1]
    lang2 = lang_menu(languages, direction="to")
    languages[lang1] = lang_name1
    if lang2 == "B":
        return 0
    lang_name2 = languages[lang2]

    rand_bindings = {
            "Y":("To randomize",None),
            "N":(f"To translate from {lang_name1} to {lang_name2}", None),
            "B":("To go back",None)}
    randomize = menu("Randomize to and from each time", rand_bindings)
    if randomize == "B":
        return 0

    langs = [lang1, lang2]
    streak = play(langs, (randomize == "Y"), modes)
    
    return streak 

def menu(title, bindings):
    while True:
        print(f"{title}:")
        print(f"Press:")
        for key, (description, function) in bindings.items():
            print(f"  {key.upper()}: {description}")
        i = input().upper()
        if i not in bindings.keys():
            print("Unknown key entered!")
            continue
        function = bindings[i][1]
        if function != None:
            ret = function()
            return (i, ret) 
        return i

#print everything as upper case if enraged!
_print = print 
def print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
    rage = get_from_inventory("R") >= 1
    if not rage:
        return _print(*objects, sep=sep, end=end,file=file,flush=flush)
    upper_objects = []
    for obj in objects:
        try:
            to_add = str(obj).upper()
        except:
            to_add = obj 
        upper_objects += [to_add]
    return _print(*upper_objects, sep=f"!{sep}", end=end,file=file,flush=flush)

def get_inventory_file_name(item_code):
    return f"inv_{item_code}.txt"

def get_from_inventory(item_code):
    file_name = get_inventory_file_name(item_code)
    value = get_variable(file_name, int, default = 0)
    return value

def add_to_inventory(item_code,number):
    current_number = get_from_inventory(item_code)
    file_name = get_inventory_file_name(item_code)
    save_variable(file_name, current_number + number)

def shop_menu():
    shop_bindings = dict()
    for item_code, (item_name, item_price) in items.items():
        shop_bindings[item_code] = (f"To buy \"{item_name}\" for {item_price} point(s)",None)
    shop_bindings["B"] = ("To go back",None)
    points_file_name = get_variable_file_name("points")
    while True:
        points = get_variable(points_file_name,int,default=0)
        print(f"Points: {points}")
        item_code = menu("Shop menu", shop_bindings)
        if item_code == "B":
            return
        item_price = items[item_code][1]
        if points < item_price:
            print("Not enough points for that!")
            continue
        add_to_inventory(item_code, 1)
        points -= item_price
        save_variable(points_file_name, points)

def add_menu():
    mode_bindings = {
            "W":("To add words",None),
            "S":("To add sentances",None),
            "B":("To go back",None)}
    modes = menu("Add menu", mode_bindings)
    if modes == "B":
        return
    mode = "word"

    if modes == "S":
        mode = "sentance"
    while True:
        print(f"Add {mode} menu:")
        to_add_list = []
        for lang_code, lang_name in languages.items():
            print(f"  Write the {mode} in the {lang_name} language (B for back): ")
            to_add = input(" >")
            if to_add.upper() == "B":
                return
            file_name = get_lang_mode_file_name(lang_code, modes)
            to_add_list += [(file_name, to_add)]
            
        for file_name, to_add in to_add_list:
            add_to_list(file_name, to_add)
        more_bindings = {
                "Y":("To add more",None),
                "N":(f"To return",None)}
        more = menu("Add more menu", more_bindings)
        if more == "N":
            break 

def show_inventory():
    print("Inventory:")
    for item_code, (item_name, item_price) in items.items():
        number = get_from_inventory(item_code)
        print(f"  {item_name}: {number}")

def main_menu():
    bindings = {
            "P":("To play", play_menu),
            "S":("To shop", shop_menu),
            "A":("To add new words, sentances or languages", add_menu),
            "I":("To show inventory", show_inventory),
            "Q":("To quit",None)}
    while True:
        ret = menu("main menu", bindings)

        if ret == "Q":
            if get_from_inventory("R") > 0:
                add_to_inventory("R",-1)
            quit(0)

     
def main():
    main_menu()

if __name__ == "__main__":
    main()
