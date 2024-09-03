import random
import sqlite3
import hashlib

class Login(object):

    def __init__(self):
        self.create_db()
        self.choice = input("1.Login 2.Register\n").strip()
        while self.choice not in ['1','2']:
            self.choice = input("1.Login 2.Register\n").strip()

        username = input("username")
        password = input("password")

        self.login(username, password) if self.choice == '1' else self.register(username, password)
            

    def create_db(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
            )
    
        connection.commit()
        connection.close()

    def register(self, username, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try: 
            cursor.execute("Insert Into users (username, password) Values (?, ?)", (username, hashed_password))
            conn.commit()
            print('User registered')
        except:
            print("username is already taken")
        
        finally:
            cursor.close()
            conn.close()
    
    def login(self, username, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()

        if user:
            print("Login successful!")
        else:
            print("Invalid username or password.")

        cursor.close()
        conn.close()



class Artifact(object):

    def __init__ (self,artifact):
        self.main = None
        self.substats = []
        self.possible_stats = {"Hp": 6, "Atk": 6, "Def": 6, "Hp%": 4, "Atk%": 4, "Def%": 4, "Er": 4, "Em": 4, "Cr": 3, "Cd": 3} # weights of the substats
        self.double = 6.5 
        self.four_substats = 20
        self.level = 0
        self.artifact = artifact
        self.path = {}
        artifact_methods = {'flower': self.generate_flower, 'feather': self.generate_feather, 'sands': self.generate_sands, 'goblet': self.generate_goblet, 'circlet': self.generate_circlet}
        artifact_methods.get(artifact)() # need the brackets here not in the dict - error
        self.convert()
        self.rolling()
       
        self.main_stats = { "Hp": 4780, "Atk": 311, "Hp%": 46.6, "Atk%": 46.6, "Def%": 58.3, "Em": 186.5, "Er": 51.8, "Pyro DMG Bonus%": 46.6, "Hydro DMG Bonus%": 46.6, "Electro DMG Bonus%": 46.6, "Cryo DMG Bonus%": 46.6, "Geo DMG Bonus%": 46.6, "Dendro DMG Bonus%": 46.6, "Anemo DMG Bonus%": 46.6, "Physical DMG Bonus%": 58.3, "Cr": 31.1, "Cd": 62.2, "Healing Bonus%": 35.9 }
        self.main_d = {self.main: self.main_stats[self.main]}
    

    def generate_flower(self):
        self.main = "Hp"
        self.roll()

    def generate_feather(self):
        self.main = "Atk"
        self.roll()
    
    def generate_sands(self):
        probabilities = { "Hp%": 26.68, "Atk%": 26.66, "Def%": 26.66, "Er": 10.00, "Em": 10.00 }
        self.cumulative(probabilities)

        self.roll()
    
    def generate_goblet(self):
        probabilities = { "Hp%": 19.25, "Atk%": 19.25, "Def%": 19, "Pyro DMG Bonus%": 5.00, "Electro DMG Bonus%": 5.00, "Cryo DMG Bonus%": 5.00, "Hydro DMG Bonus%": 5.00, "Dendro DMG Bonus%": 5.00, "Anemo DMG Bonus%": 5.00, "Geo DMG Bonus%": 5.00, "Physical DMG Bonus%": 5.00, "Em": 2.50 }
        self.cumulative(probabilities)
        self.roll()

    def generate_circlet(self):
        probabilities = {"Hp%": 22.00, "Atk%": 22.00, "Def%": 22.00, "Cr": 10.00, "Cd": 10.00, "Healing Bonus%": 10.00, "Em": 4.00}
        self.cumulative(probabilities)
        self.roll()


    def cumulative(self, probabilities):
        cumulative_probs = {}
        current_sum = 0
        for key, prob in probabilities.items():
            current_sum += prob
            cumulative_probs[key] = current_sum
        roll = random.randint(0,100)
        for stat, cumulative_prob in cumulative_probs.items():
            if roll <= cumulative_prob:
                self.main = stat
                break
    

    def roll(self):
        if random.randint(0,100) <= self.four_substats:
            self.num = 4
        else: 
            self.num = 3
            self.level =-1
        self.roll_odds(self.num)


    def roll_odds(self, num, var = True):
        for i in range(num):
            self.others = 0
            for key,value in self.possible_stats.items():
                self.others += value

            self.chances = [] # list of percentages
            for key in self.possible_stats.keys():
                if key in self.substats or key == self.main:
                    continue
                self.chances.append([key, self.possible_stats[key] / self.others])
            stats = [item[0] for item in self.chances]
            probs = [item[1] for item in self.chances]
            # Use random.choices to pick based on the probabilities
            stat = random.choices(stats, weights=probs, k=1)[0]
            self.substats.append(stat) # [0] cause random.choices still returns a list
            self.path[stat] = 0
        return stat

    def convert(self):
        self.stats = {}
        for i in self.substats:
            self.stats[i] = 0

    def rolling(self):
        if self.level == -1:
            # roll a fourth substat
            stat = self.roll_odds(1, False)
            self.level = 4

        # init values
        self.odds = [25, 50, 75, 100]
        attributes = { "Hp": [209.13, 239.00, 268.88, 298.75], "Atk": [13.62, 15.56, 17.51, 19.45], "Def": [16.20, 18.52, 20.83, 23.15], "Hp%": [4.08, 4.66, 5.25, 5.83], "Atk%": [4.08, 4.66, 5.25, 5.83], "Def%": [5.10, 5.83, 6.56, 7.29], "Em": [16.32, 18.65, 20.98, 23.31], "Er": [4.53, 5.18, 5.83, 6.48], "Cr": [2.72, 3.11, 3.50, 3.89], "Cd": [5.44, 6.22, 6.99, 7.77] }

        for i in self.substats:
            num = random.randint(0,100)
            for j in range(len(self.odds)):
                if num <= self.odds[j]:
                    num = j
                    break   
            self.stats[i] = attributes[i][num]
            self.path[i] += attributes[i][num]
    
        self.weights = []
        self.others = 0
        for i in self.substats:
            self.others += self.possible_stats[i]
        
        for i in self.substats:
            self.weights.append([i, self.possible_stats[i] / (self.others)])

        values = [i[0] for i in self.weights]
        prob = [i[1] for i in self.weights]
        for i in range(self.level + 4, 21, 4):
            choice = random.choices(values, weights=prob, k = 1)[0]
            # update said choice var
        
            num = random.randint(0,2)
            if num == 0: mult = 0.7
            elif num == 1: mult = 0.8
            else: mult = 0.9
            self.stats[choice] += attributes[choice][-1] * mult
            
    
    def display(self):
        print(f"{self.artifact.capitalize()} Main: {self.main_stats[self.main]} {self.main}, CV: {self.crit_value(self.main)}")
        for i in self.stats.keys():
            add = ''
            if i == "Cr" or i == "Cd" or i == "Er" or "%" in i:
                add = '%'
            print(f"{i}: {self.stats[i]:.2f}{add}")
        print()
    
    def crit_value(self, main_stat=None):
        #main stats matter more
        if main_stat is not None and self.main != main_stat:
            return 0
        cv = 0
        if "Cr" in self.substats:
            cv += self.stats['Cr'] * 2
        if "Cd" in self.substats:
            cv += self.stats['Cd']
        return round(cv,2)

    def add_to_path(self, path):
        self.path.append(path)

    def print_path(self):
        print(self.path)
        

class Roll(object):

    def __init__(self, times, goblet_main =None, circlet_main=None):
        self.flower = None
        self.feather = None
        self.sands = None
        self.goblet = None
        self.circlet = None
        self.times = times
        self.stats = {"Cr": 0, "Cd": 0, "Er": 0, "Em": 0}
        self.goblet_main = goblet_main
        self.circlet_main = circlet_main
        

    def roller(self):
        return {0: "flower", 1: "feather", 2:"sands", 3: "goblet", 4: "circlet"}[random.randint(0,4)]

    def in_roll(self):
        gear = self.roller()
        artifact = Artifact(gear)
        if len(artifact.substats ) <= 3:
            print(artifact)
            exit() 
        gear_map = { "flower": "flower", "feather": "feather", "sands": "sands", "goblet": "goblet", "circlet": "circlet" }
        if gear in gear_map:
            current_gear = getattr(self, gear_map[gear]) # this is basically "self.gear_map[gear]"
            if current_gear is None:
                setattr(self, gear_map[gear], artifact)
            elif gear == "circlet":
                if artifact.crit_value("Cr") > current_gear.crit_value(current_gear.main) or artifact.crit_value("Cd") > current_gear.crit_value(current_gear.main):
                    setattr(self, "circlet", artifact) # self.circlet = artifact
            
            elif gear == "goblet":
                if artifact.crit_value("Pyro DMG Bonus%") > current_gear.crit_value(current_gear.main):
                    setattr(self, "goblet", artifact)


            elif current_gear is None or artifact.crit_value() > current_gear.crit_value():
                setattr(self, gear_map[gear], artifact)


    def total_stats (self,artifact):
        for i in artifact.stats.keys():
            if i in self.stats:
                self.stats[i] += artifact.stats[i]
        if artifact.main in self.stats:
            self.stats[artifact.main] += artifact.main_stats[artifact.main]

    
    def end_stats(self):
        for key,value in self.stats.items():
            add = ''
            if key != 'Em':
                add = "%"
            x=0
            if key == 'Cr': x = 5
            if key == 'Cd': x = 50
            print(f"Total {key} is {value + x:.2f}{add}")
            

    def loop(self):
        for _ in range(0, self.times):
            self.in_roll()
            if random.randint(0,100) <= 6.5:
                self.in_roll()


        self.flower.display() if self.flower is not None else print("No flower")
        self.feather.display() if self.feather is not None else print("No feather")
        self.sands.display() if self.sands is not None else print("No sands")
        self.goblet.display() if self.goblet is not None else print("No goblet")
        self.circlet.display() if self.circlet is not None else print("No circlet")

        self.total_stats(self.flower) if self.flower is not None else None
        self.total_stats(self.feather) if self.feather is not None else None
        self.total_stats(self.sands) if self.sands is not None else None
        self.total_stats(self.goblet) if self.goblet is not None else None
        self.total_stats(self.circlet) if self.circlet is not None else None
        self.end_stats()
        

def main(): 
    login = Login()
    roll = Roll(200)
    roll.loop()

        

if __name__ == "__main__":
    main()

