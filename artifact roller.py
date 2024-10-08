import random
import sqlite3
import hashlib
import math

class Login(object):

    def __init__(self):
        self.save_one = False
        # self.drop()
        self.options_for_artifacts = { "flower": "flower", "feather": "feather", "sands": "sands", "goblet": "goblet", "circlet": "circlet" }

        self.create_db()
        self.info()
        while not (self.login(self.username, self.password) if self.choice == '1' else self.register(self.username, self.password)):
            self.info()
    
    def drop(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS flower")
        cursor.execute("DROP TABLE IF EXISTS feather")
        cursor.execute("DROP TABLE IF EXISTS sands")
        cursor.execute("DROP TABLE IF EXISTS goblet")
        cursor.execute("DROP TABLE IF EXISTS circlet")
        cursor.close()
        connection.close()


    def create_db(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY UNIQUE NOT NULL,
            password TEXT NOT NULL,
            resin_used INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            '''
            )
        
        self.create_artifacts('feather')
        self.create_artifacts('flower')
        self.create_artifacts('sands')
        self.create_artifacts('goblet')
        self.create_artifacts('circlet')
        
        connection.commit()
        connection.close()

    def create_artifacts(self,artifact):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(f''' 
            CREATE TABLE IF NOT EXISTS {artifact} (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id TEXT NOT NULL, -- this is the same as username in users table
            main_stat TEXT DEFAULT 'atk',
            main_stat_value FLOAT NOT NULL,
            substat_1_name TEXT NOT NULL,
            substat_1_value FLOAT NOT NULL,
            substat_2_name TEXT NOT NULL,
            substat_2_value FLOAT NOT NULL,
            substat_3_name TEXT NOT NULL,
            substat_3_value FLOAT NOT NULL,
            substat_4_name TEXT NOT NULL,
            substat_4_value FLOAT NOT NULL,
            crit_value FLOAT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
            )
            ''')
        conn.commit()
        cursor.close()
        conn.close()

    
    def info(self):
        self.choice = input("1.Login 2.Register\n").strip()
        while self.choice not in ['1','2']:
            self.choice = input("1.Login 2.Register\n").strip()

        self.username = input("username\n")
        self.password = input("password\n")

    def register(self, username, password):
        success = False
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try: 
            cursor.execute("Insert Into users (username, password) Values (?, ?)", (username, hashed_password))
            conn.commit()
            print('User registered')
            success = True
        except:
            print("username is already taken")
        
        finally:
            cursor.close()
            conn.close()
            return success
    
    def login(self, username, password):
        success = False
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()

        if user:
            print("Login successful!")
            success = True
        else:
            print("Invalid username or password.")

        cursor.close()
        conn.close()
        return success


    def menu(self):
        choice = input("1. View resin spent \n2. Roll n times\n3. View best artifacts\n4. turn on/off 'save best only'\n5. View leaderboards for top resin used\n")
        if choice == '1':
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # get the resin
            result = cursor.execute("SELECT resin_used FROM users WHERE username = ?", (self.username,)).fetchone()[0]
            print(f"You have spent a total of {result} resin")
            cursor.close()
            conn.close()
        elif choice == '2':
            while True:
                try:
                    amount = int(input("How many times would you like to roll\n"))
                    if amount > 0 and amount < 5000000:
                        break
                    else:
                        print("Enter a valid number (greater than 0, less than 5000000)")
                except ValueError:
                    print("Please enter a valid integer.")

            self.add_resin(amount * 20)
            roll = Roll(amount, self.username, self)
            roll.loop()
        
        elif choice == '3':
            choice = input("Which artifact would you like to see? type 'all' to see all your best artifacts\n").lower().strip()
            while choice not in ['flower', 'feather', 'sands', 'goblet', 'circlet', 'all']:
                    choice = input("Which artifact would you like to save? Make sure you spell it correctly!\n").lower().strip()
            result = self.view_artifacts(self.options_for_artifacts[choice],True)
            if not result:
                print(f"No {choice} currently saved")
            else:
                print(f"\n{choice.capitalize()} Main: {result[2]} {result[3]} CV: {result[-1]}")
                for i in range(4, len(result) - 1, 2):
                    print(f"{result[i]}:{result[i+1]: .2f}")
        elif choice == '4':
            self.save_one = not self.save_one
            print(f"you have turned {'off' if self.save_one else 'on'} save many artifacts")
        
        elif choice == '5':
            self.resin_leaderboards()
        
        self.menu()
    
    def resin_leaderboards(self):
        while True:
            try:
                amount = int(input("How many top resin users would you like to see?\n"))
                if amount <= 0 or amount > 100:
                    print("You must enter a number between 1-100\n")
                else:
                    break
            except:
                print("please enter a number")
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        query = f'''
                SELECT username, resin_used 
                FROM users 
                ORDER BY resin_used DESC 
                LIMIT {amount};
                '''
        result = cursor.execute(query, ()).fetchall()
        for i in range(len(result)):
                print(f"User {result[i][0]} has spent a total of {result[i][1]} resin! Thats a total of {math.floor(result[i][1] / 200): .0f} Days!!")
        print()

        cursor.close()
        conn.close()


    def add_resin(self, amount):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # get the resin
        result = cursor.execute("SELECT resin_used FROM users WHERE username = ?", (self.username,)).fetchone()[0]
        # update the resin amount
        if result is None:
            result = 0
        cursor.execute("UPDATE users SET resin_used = ? where username = ?", (result + amount, self.username))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"resin before is {result} and updated resin is {result + amount}")
        
    
    def view_artifacts(self,name, viewer = False):
        conn = sqlite3.connect(f'users.db')
        cursor = conn.cursor()
        if viewer:
            if name == 'feather' or name == 'flower':
                search = 'Atk' if name == 'feather' else 'Hp'
            else:
                choice = input(f"What main stat would you like to see that has the best CV for {name}\n")
                search = choice
            result = cursor.execute(f'''SELECT * FROM {name} WHERE user_id = ? 
                                    ORDER BY 
                                        CASE WHEN main_stat = ? THEN 1 ELSE 0 END DESC, 
                                        crit_value DESC  
                                    LIMIT 1''', (self.username, search)).fetchone()
                        
        else:
            query = f'''
                    SELECT *
                    FROM {name}
                    WHERE user_id = ?
                    '''
            result = cursor.execute(query, (self.username,)).fetchall()

        

        cursor.close()
        conn.close()
        return result

    def save_artifacts(self, name, artifact, going_for = None):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        def search(conn, cursor):
            where_clause = 'WHERE main_stat = ?' if going_for is not None else ''
            query = f'''
                SELECT crit_value 
                FROM {name} 
                {where_clause}
                ORDER BY crit_value DESC 
                LIMIT 1
            '''

            if going_for is not None:
                res = cursor.execute(query, (going_for,)).fetchone()
                return res[0] if res is not None else 0
            return 0
            #else:
            #    res = cursor.execute(query).fetchone()

            return res[0] if res is not None else 0
        if self.save_one and(search(conn, cursor) > artifact.crit_value(artifact.main)):
            return

        query = f'''
                INSERT INTO {name}
                (main_stat, main_stat_value,
                substat_1_name, substat_1_value, 
                substat_2_name, substat_2_value, 
                substat_3_name, substat_3_value, 
                substat_4_name, substat_4_value,
                crit_value, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
            '''
        
        li = []
        for key, value in artifact.stats.items():
            li.append([key, value])
        
        values = (artifact.main, artifact.main_stats[artifact.main],
                li[0][0], li[0][1], 
                li[1][0], li[1][1], 
                li[2][0], li[2][1], 
                li[3][0], li[3][1], 
                artifact.crit_value(artifact.main),
                self.username)
        
        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()


class Artifact(object):

    def __init__ (self,artifact,login):
        self.main = None
        self.substats = []
        self.possible_stats = {"Hp": 6, "Atk": 6, "Def": 6, "Hp%": 4, "Atk%": 4, "Def%": 4, "Er": 4, "Em": 4, "Cr": 3, "Cd": 3} # weights of the substats
        self.double = 6.5 
        self.four_substats = 20
        self.level = 0
        self.artifact = artifact
        self.path = {}
        self.login = login
        artifact_methods = {'flower': self.generate_flower, 'feather': self.generate_feather, 'sands': self.generate_sands, 'goblet': self.generate_goblet, 'circlet': self.generate_circlet}
        artifact_methods.get(artifact)() # need the brackets here not in the dict - error
        self.convert()
        self.rolling()
       
        self.main_stats = { "Hp": 4780, "Atk": 311, "Hp%": 46.6, "Atk%": 46.6, "Def%": 58.3, "Em": 186.5, "Er": 51.8, "Pyro DMG Bonus%": 46.6, "Hydro DMG Bonus%": 46.6, "Electro DMG Bonus%": 46.6, "Cryo DMG Bonus%": 46.6, "Geo DMG Bonus%": 46.6, "Dendro DMG Bonus%": 46.6, "Anemo DMG Bonus%": 46.6, "Physical DMG Bonus%": 58.3, "Cr": 31.1, "Cd": 62.2, "Healing Bonus%": 35.9 }
        self.main_d = {self.main: self.main_stats[self.main]}
    

    def login_setup(self, var):
         self.log = var
    

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

    def __init__(self, times, login, login_class, goblet_main =None, circlet_main=None):
        self.login_class = login_class
        self.flower = None
        self.feather = None
        self.sands = None
        self.goblet = None
        self.circlet = None
        self.login = login
        self.times = times
        self.stats = {"Cr": 0, "Cd": 0, "Er": 0, "Em": 0}
        self.goblet_main = goblet_main
        self.circlet_main = circlet_main
        self.gear_map = { "flower": "flower", "feather": "feather", "sands": "sands", "goblet": "goblet", "circlet": "circlet" }
        
        self.sands_choice = ''
        self.goblet_choice = ''
        self.circlet_choice = ''

        self.sands_attr = {1: "Em", 2: "Er", 3: "Def%", 4: "Atk%", 5: "Hp%"}
        self.goblet_attr = {1: "Em", 2: "Physical DMG Bonus%", 3: "Geo DMG Bonus%", 4: "Anemo DMG Bonus%", 5: "Dendro DMG Bonus%", 6: "Hydro DMG Bonus%", 7: "Cryo DMG Bonus%", 8: "Electro DMG Bonus%", 9: "Pyro DMG Bonus%", 10: "Def%", 11: "Atk%", 12: "Hp%"}
        self.circlet_attr = {1: "Em", 2: "Healing Bonus%", 3: "Cd", 4: "Cr", 5: "Def%", 6: "Atk%", 7: "Hp%"}
        self.choose_main(0)

    
    def choose_main(self, i):
        attributes = [
            ("sands", self.sands_attr),
            ("goblet", self.goblet_attr),
            ("circlet", self.circlet_attr)
        ]

        while i < len(attributes):
            attr_name, attr_dict = attributes[i]
            try:
                choice = input(f"Enter a main {attr_name} stat you would like. Put 'any' for any stat {attr_dict}\n")
                if choice == 'any' or choice == 'a':
                    setattr(self, f"{attr_name}_choice", 'any')
                elif int(choice) not in attr_dict.keys():
                    continue
                else:
                    setattr(self, f"{attr_name}_choice", attr_dict[int(choice)])
                i += 1
            except ValueError:
                print("Invalid input. Please enter a valid number or 'any'.")
        while True:
            try:
                choice = int(input("What is the minimum crit value that you would like to save for these pieces? Note only >= crit value pieces will be stored\n"))
                if choice < 0 or choice >= 60:
                    print("getting that crit value is impossible")
                self.crit_amount = choice
                break

            except:
                print("that is not a valid number")


    def roller(self):
        return {0: "flower", 1: "feather", 2:"sands", 3: "goblet", 4: "circlet"}[random.randint(0,4)]

    def in_roll(self):
        gear = self.roller()
        artifact = Artifact(gear,self.login)
        if len(artifact.substats ) <= 3:
            print(artifact)
            exit() 
        if gear in self.gear_map:
            current_gear = getattr(self, self.gear_map[gear]) # this is basically "self.gear_map[gear]"
            if current_gear is None:
                setattr(self, self.gear_map[gear], artifact)
            elif gear == "sands":
                if artifact.crit_value(self.sands_choice if self.sands_choice != 'any' else None) > self.crit_amount:
                    self.login_class.save_artifacts("sands", artifact, self.sands_choice)

                if artifact.crit_value(self.sands_choice if self.sands_choice != 'any' else None) > current_gear.crit_value(current_gear.main):
                    setattr(self, "sands", artifact)
            
            elif gear == "goblet":
                if artifact.crit_value(self.goblet_choice if self.goblet_choice != 'any' else None) >= self.crit_amount:
                    self.login_class.save_artifacts("goblet", artifact, self.goblet_choice)

                if artifact.crit_value(self.goblet_choice if self.goblet_choice != 'any' else None) >= current_gear.crit_value(current_gear.main):
                    setattr(self, "goblet", artifact)

            elif gear == "circlet":
                if artifact.crit_value(self.circlet_choice if self.circlet_choice != 'any' else None) >= self.crit_amount:
                    self.login_class.save_artifacts("circlet", artifact,self.circlet_choice)

                if artifact.crit_value(self.circlet_choice if self.circlet_choice != 'any' else None) > current_gear.crit_value(current_gear.main):
                    setattr(self, "circlet", artifact) # self.circlet = artifact

            # elif current_gear is None or artifact.crit_value() > current_gear.crit_value(): # for flowers and feathers
            #     setattr(self, self.gear_map[gear], artifact)
            
            elif gear == "flower":
                if artifact.crit_value(artifact.main) > current_gear.crit_value(current_gear.main):
                    self.login_class.save_artifacts("flower", artifact)
            elif gear == "feather":
                 if artifact.crit_value(artifact.main) > current_gear.crit_value(current_gear.main):
                    self.login_class.save_artifacts("feather", artifact, )


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
        self.save()

    
    def save(self):
        while True:
            choice = input("Would you like to add any of these artifacts into your saved collection? Y/N\n").lower().strip()
            if choice == 'n' or choice == 'no':
                return

            elif choice == 'y' or choice == 'yes':
                choice2 = input("Which artifact would you like to save?\n").lower().strip()
                while choice2 not in ['flower', 'feather', 'sands', 'goblet', 'circlet']:
                    choice2 = input("Which artifact would you like to save? Make sure you spell it correctly!\n").lower().strip()
                self.login_class.save_artifacts(choice2, getattr(self, self.gear_map[choice2]))
                print(f"Succesfully saved {choice2}.")
        

def main(): 
    login = Login()
    login.menu()

if __name__ == "__main__":
    main()