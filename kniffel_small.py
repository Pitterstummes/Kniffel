import random

class Scoreboard:
    def __init__(self):
        self.fields = {
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
        self.freefields = [1, 2, 3, 4, 5, 6] # Indices of the free fields
        self.goalpoints = [3, 6, 9, 12, 15, 18] # Goal points for the free fields

    def update_score(self, field, points):
        # Update the score for a specific field
        self.fields[field] = points
        self.freefields.remove(field)   # Remove the field from the list of free fields
        
    def calculate_scores(self):
        # Calculate the sum, bonus, and total scores based on the individual fields
        if None not in self.fields[1:7]:
            self.fields["sum"] = sum(self.fields[1:7])
            if self.fields["sum"] >= 63:
                self.fields["bonus"] = 37
            else:
                self.fields["bonus"] = 0
            
            self.fields["total_1"] = self.fields["sum"] + self.fields["bonus"]

    def calculate_occurances(self, dice):
        # Calculate the number of occurances of each value
        occurances = [dice.count(i) for i in range(1, 7)]
        return occurances
    
    
