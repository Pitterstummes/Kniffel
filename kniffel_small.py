import random

fields = {
    "name": None,           # 00 Name of the player
    "ones": None,           # 01 Score for ones
    "twos": None,           # 02 Score for twos
    "threes": None,         # 03 Score for threes
    "fours": None,          # 04 Score for fours
    "fives": None,          # 05 Score for fives
    "sixes": None,          # 06 Score for sixes
    "sum": None,            # 07 Sum of the first six fields
    "bonus": None,          # 08 Bonus points
    "total_1": None         # 09 Total score for the first part
    }
freefields = [1, 2, 3, 4, 5, 6] # Indices of the free fields
maxpoints = [5, 10, 15, 20, 25, 30] # Maximum points for the free fields
# goalpoints = [3, 6, 9, 12, 15, 18] # Goal points for the free fields

def update_score(field, points):
    # Update the score for a specific field
    fields[field] = points
    freefields.remove(field)   # Remove the field from the list of free fields
    
def calculate_scores():
    # Calculate the sum, bonus, and total scores based on the individual fields
    if None not in fields[1:7]:
        fields["sum"] = sum(fields[1:7])
        if fields["sum"] >= 63:
            fields["bonus"] = 37
        else:
            fields["bonus"] = 0
        
        fields["total_1"] = fields["sum"] + fields["bonus"]

def calculate_occurances(dice):
    # Calculate the number of occurances of each value
    occurances = [dice.count(i) for i in range(1, 7)]
    return occurances

def writename(name):
    # Write the name of the player
    fields["name"] = name


