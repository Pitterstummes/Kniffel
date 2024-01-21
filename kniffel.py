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
            "total_1": None,        # 09 Total score for the first part
            "one_pair": None,       # 10 Score for one pair
            "two_pairs": None,      # 11 Score for two pairs
            "triple": None,         # 12 Score for three of a kind
            "quad": None,           # 13 Score for four of a kind
            "full_house": None,     # 14 Score for full house
            "small_street": None,   # 15 Score for small street
            "big_street": None,     # 16 Score for big street
            "kniffel": None,        # 17 Score for kniffel
            "chance": None,         # 18 Score for chance
            "total_2": None,        # 19 Total score for the second part
            "total": None           # 20 Total score
        }
        self.freefields = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18] # Indices of the free fields

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
         
        if None not in self.fields[10:19]:
            self.fields["total_2"] = sum(self.fields[10:19])
        
        if None not in self.fields["total_1"] and self.fields["total_2"]:
            self.fields["total"] = self.fields["total_1"] + self.fields["total_2"]


class Dice:
    def __init__(self):
        self.values = []  # List to store the values of the dice

    def roll(self):
        # Roll the dice to get random values
        pass
        

    def keep(self, indices):
        # Keep the dice at the specified indices
        pass

    def reroll(self, indices):
        # Reroll the dice at the specified indices
        pass


class Game:
    def __init__(self):
        self.scoreboard = Scoreboard()
        self.dice = Dice()


    def play(self):
            # Main game loop
            while len(self.scoreboard.freefields) > 0:
                # Roll the dice
                self.dice.roll()

                # Calculate the best possible scores for all free fields
                for field in self.scoreboard.freefields:
                    # Calculate the score for the current field
                    score = calculate_best_score(self.dice.values, field)

                    # Update the score in the scoreboard
                    self.scoreboard.update_score(field, score)

                # Write points to the scoreboard (end of turn)
                self.write_points_to_scoreboard()

    def calculate_best_score(dice_values, field):
        # Calculate the best possible score for the given dice values and field
        # Implement your logic here
        pass

    def write_points_to_scoreboard(self):
        # Write the points to the scoreboard
        # Implement your logic here
        pass


# Create an instance of the game and start playing
game = Game()
game.play()
