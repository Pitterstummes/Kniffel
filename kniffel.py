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
        self.goalpoints = [3, 6, 9, 12, 15, 18, 12, 22, 18, 24, 30, 25, 40, 50, 22] # Goal points for the free fields

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

    def first_roll(self):
        # Roll the dice to get random values
        random_integers = [random.randint(1, 6) for _ in range(5)]
        self.values = random_integers

    def keep(self, indices):
        # Keep the dice at the specified indices
        pass

    def reroll(self, indices):
        # Reroll the dice at the specified indices
        pass

    def calc_score_1_to_6(self, values, field):
        # Calculate the score for scoreboard indices 1 to 6: ones till sixes
        return sum(value for value in values if value == field)

    def calc_score_10(self, values):
        # Calculate the score for scoreboard index 10: one pair
        pairs = []
        for value in set(values):
            if values.count(value) >= 2:
                pairs.append(value)
        if pairs:
            highest_pair = max(pairs)
            return highest_pair * 2
        else:
            return 0
        
    def calc_score_11(self, values):
        # Calculate the score for scoreboard index 11: two pairs
        pairs = []
        for value in set(values):
            if values.count(value) >= 2:
                pairs.append(value)
        if len(pairs) >= 2:
            return sum(pairs) * 2
        else:
            return 0
        
    def calc_score_12(self, values):
        # Calculate the score for scoreboard index 12: three of a kind
        for value in set(values):
            if values.count(value) >= 3:
                return value * 3
        return 0
    
    def calc_score_13(self, values):
        # Calculate the score for scoreboard index 13: four of a kind
        for value in set(values):
            if values.count(value) >= 4:
                return value * 4
        return 0
    
    def calc_score_14(self, values):
        # Calculate the score for scoreboard index 14: full house
        for value in set(values):
            if values.count(value) == 3:
                for value2 in set(values):
                    if value2 != value and values.count(value2) == 2:
                        return 30
        return 0
    
    def calc_score_15(self, values):
        # Calculate the score for scoreboard index 15: small street
        if set(values) in [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]:
            return 25
        else:
            return 0
        
    def calc_score_16(self, values):
        # Calculate the score for scoreboard index 16: big street
        if set(values) in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]:
            return 40
        else:
            return 0
        
    def calc_score_17(self, values):
        # Calculate the score for scoreboard index 17: kniffel
        for value in set(values):
            if values.count(value) == 5:
                return 50
        return 0
    
    def calc_score_18(self, values):
        # Calculate the score for scoreboard index 18: chance
        return sum(values)
    
    def calc_score_field(self, values, field):
        # Calculate the score for the given values and field
        match field:
            case 1 | 2 | 3 | 4 | 5 | 6:  # Ones till sixes
                return Dice.calc_score_1_to_6(values, field)
            case 10:    # One pair
                return Dice.calc_score_10(values)
            case 11:    # Two pairs
                return Dice.calc_score_11(values)
            case 12:    # Three of a kind
                return Dice.calc_score_12(values)
            case 13:    # Four of a kind
                return Dice.calc_score_13(values)
            case 14:    # Full house
                return Dice.calc_score_14(values)
            case 15:    # Small street
                return Dice.calc_score_15(values)
            case 16:    # Big street
                return Dice.calc_score_16(values)
            case 17:    # Kniffel
                return Dice.calc_score_17(values)
            case 18:    # Chance
                return Dice.calc_score_18(values)
            case _:     # Invalid field
                raise TypeError("Invalid field")
    



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
                    score = Game.calculate_best_score(self.dice.values, field)

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

    def print_scoreboard(self):
        # Print the scoreboard
        # Implement your logic here
        pass


# Create an instance of the game and start playing
game = Game()
game.play()

