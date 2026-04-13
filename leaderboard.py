import json
import os 
from datetime import datetime


RECORDS_FILE = os.path.join(os.path.dirname(__file__), "data", "records.json")

#top scores to keep
MAX_RECORDS = 5

def load_records():
    # if the file doesn't exist yet (first run),
    # return an empty list instead of crashing
    try:
        with open(RECORDS_FILE, "r") as f:
            return json.load(f)
        # reads JSON data from a file and converts it into the corresponding Python object (this case as RECORDS_FILE as f)
        # json.load(f) converts the JSON file into a Python dictionary.
        # if there isn't files to read, return an empty list
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_records(score, stage, wave):
    #saving the current score, stage, wave

    #load existing records
    records = load_records()

    #build new entry, datetime.now() gives current time — strftime formats it as a readable string
    entry = {
        "score": score,
        "stage": stage,
        "wave":  wave,
        "date":  datetime.now().strftime("%Y-%m-%d  %H:%M")
    }
    
    records.append(entry)
    records = bubblesorting(records)

    records = records[:MAX_RECORDS]
    #keeping only top records
    os.makedirs(os.path.dirname(RECORDS_FILE), exist_ok=True)
    #making sure the folder exists
    with open(RECORDS_FILE, "w") as f:
        #indent=2 makes the JSON file readable
        json.dump(records, f, indent=2)
 
    return records  #return the updated list
def is_new_record(score):
    # returns True if this score is high to be in top
    records = load_records()
    if len(records) < MAX_RECORDS:
        return True   # fewer than max entries = always qualifies
    return score > records[-1]["score"]   #better than the lowest saved score
def bubblesorting(records):
    #use bubble sort method to place the recorded points form the highest to lowest records[0] -> records[len - 1]
    n = len(records)
    # length of the records for how many attempts in sorting, O(n^2)
    for pass_num in range(n):
        #n - pass_num - 1:
        #after each pass, the smallest value has sunk to the end
        #so don't need to check that last position again
        #pass 0 checks all pairs, pass 1 checks one fewer, and so on
        swapped = False

        for i in range(n - pass_num - 1):
            if records[i]["score"] < records[i + 1]["score"]:
                # swap the two neighbours
                records[i], records[i + 1] = records[i + 1], records[i]
                swapped = True

        #if it is a full pass with zero swaps,
        #the list is already sorted -> break, stop sorting
        if swapped == False:
            break
    return records      

# [500, 300, 900, 200, 700] example
# len = 5 pass num in range(5) passnum = [0, 1, 2, 3 ,4], 1st i in range(5 - 0 - 1 = 4); 2nd i (5 - 1 - 1 = 3)
# after each inner for loop, the smallest score/value will sunk to the end of the list
# the loop goes on till pass_numm has reached len of records - 1 or list is fully sorted                 