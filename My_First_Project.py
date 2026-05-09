import requests,re,csv
class CF_User(): 
    def __init__(self,handle,rank,rating):
        self.handle = handle
        self.rank = rank
        self.rating = rating
    def Profile_Url(self):
        return f"https://codeforces.com/profile/{self.handle}"
    @property
    def handle(self):
        return self._handle
    @handle.setter
    def handle(self,handle):
        match = re.match(r"^[A-Za-z0-9._-]{3,24}$",handle)
        if not match:
            raise ValueError("Invalid input!!!")
        self._handle = handle
    def __str__(self):
        return f"Hello {self.rank} {self._handle} with rating of: {self.rating}."
    def is_active(self):
        return int(self.rating) > 0
    



class Member(CF_User):
    def __init__(self,handle,rank="Unranked",rating=0):
        super().__init__(handle,rank,rating)
        self.submissions = []
        self.solve_count = 0
        self.favorite_tag = ""
        self.last_updated=None
        self.weaknesses=[]
        self.solved_problems_list = []
    def fetch_submissions(self):
        
        try:
            response = requests.get(f"https://codeforces.com/api/user.status?handle={self.handle}&count=40")
            data = response.json()
            #print(data)
            if data["status"]=="OK":
                self.submissions = data["result"]
                for submission in self.submissions:
                    if submission["verdict"]=="OK":
                        self.solve_count +=1
                        if "problem" in submission:
                            prob_data = submission["problem"]
                        
                            solved_problem = Problem(
                                prob_data["contestId"], 
                                prob_data["index"], 
                                prob_data["name"], 
                                prob_data["tags"])
                            self.solved_problems_list.append(solved_problem)
                self.analyze_weaknesses()
            else:
                print(f"Could not fetch submissions for {self.handle}.")
        except requests.RequestException:
            print("Error occurred while trying to fetch submissions!!!")

        
    def analyze_weaknesses(self):
        failed_topics = {}
        for sub in self.submissions: #Codeforces puts the tags inside a dictionary inside a list so I have to make a loop through it.
            if "verdict" in sub and sub["verdict"] != "OK":
                
                if "problem" in sub:
                    problem = sub["problem"]
                else:
                    problem ={}
                
                if "tags" in problem:
                    tags = problem["tags"]
                else:
                    tags = []
                for tag in tags:
                    if tag in failed_topics:
                        failed_topics[tag] +=1
                    else:
                        failed_topics[tag] =1
        # I needed to sort the dictionary by values (highest count first), 
        # so I passed the dictionary's .get method as the sorting key.
        sorted_weaknesses = sorted(failed_topics,key=failed_topics.get,reverse = True)
        self.weaknesses = sorted_weaknesses[:3]
        print(f"The top weaknesses are: {self.weaknesses}")
    def calculate_accuracy(self):
        if not self.submissions:
            print(f"No submissions found for {self.handle}.")
            self.accuracy = 0.0
            return
        else:
            total_submissions = len(self.submissions)
            self.accuracy = round((self.solve_count/total_submissions*100),2)
            print(f"The Accuracy for {self.handle} is {self.accuracy}")
    
    def fetch_practice_problem(self):#optional function
        if not self.weaknesses:
            return "No weaknesses found to recommended problem."
        weakness_1 = self.weaknesses[0]
        try:
            response = requests.get(f"https://codeforces.com/api/problemset.problems?tags={weakness_1}")
            data = response.json()
            if data["status"] =="OK":
                problems = data["result"]["problems"]
                solved_ids = []
                for prob in self.solved_problems_list:
                    solved_ids.append(prob.get_id())
                recommended = []
                for problem in problems:
                    prob_id = f"{problem['contestId']}{problem['index']}"
                    if prob_id not in solved_ids:
                        link = f"https://codeforces.com/contest/{problem['contestId']}/problem/{problem['index']}"
                        recommended.append(f"[{prob_id}] {problem['name']} -> {link}")
                    if len(recommended)==3:
                        break
                return recommended
        except requests.RequestException:
            return ["Network error while fetching recommendations."]
                    


class Problem(): 
    def __init__(self,contest_id,index,title,tags):
        self.contest_id = contest_id
        self.index  = index
        self.title = title
        self.tags = tags
    def get_id(self):
        return f"{self.contest_id}{self.index}"
    def __str__(self):
        return f"[{self.get_id()} {self.title}]"













class ScoutSystem():
    def __init__(self,group_name):
        self.group_name = group_name
        self.Members = []
        self.__api_url = "https://codeforces.com/api/"#private variable
        self.history = self.load_history()
    def load_history(self):
        history = {}
        try:
            with open("DataBase.csv","r") as csv_file:
                reader = csv.reader(csv_file)
                is_first_line = True 
                
                for row in reader:
                    if is_first_line == True:
                        is_first_line = False 
                        continue 
                for row in reader:
                    if row and row[3] != "Solve Count":
                        history[row[0]] = int(row[3])
        except FileNotFoundError:
            pass
        return history
    def add_member(self,handle):
        try:
            response = requests.get(f"{self.__api_url}user.info?handles={handle}")
            data = response.json()
            #print(data)
            if data["status"] == "OK":
                info = data["result"][0]
                if "rank" in info:
                    rank = info["rank"]
                else:
                    rank = "Unranked"
                
                
                if "rating" in info:
                    rating = info["rating"]
                else:
                    rating = 0
                new_member = Member(handle,rank,rating)
                new_member.fetch_submissions()
                new_member.calculate_accuracy()
                self.Members.append(new_member)
            else:
                print("Handle not found on Codeforces.")
        except requests.RequestException:
            print("Error occurred while trying to connect to codeforces services!!!")
        except ValueError as e:
            print(e)
    def generate_report(self):
        if len(self.Members) == 0:
            print("No members tracked yet!!!!")
            return
            
        for member in self.Members:
            print("\n" + "-"*50)
            
            # header
            
            print(f"REPORT FOR: {member.handle}")
            print(f"Current Rating: {member.rating} | Accuracy: {member.accuracy}% | Rank: {member.rank}")
            
            # --- 2. NEW VS RETURNING USER ---
            
            if member.handle in self.history:
                old_solve_count = self.history[member.handle]
                
                print(f"DEBUG: Returning user. Old solves: {old_solve_count}, New solves: {member.solve_count}")
            else:
                
                print("DEBUG: This is a new user!")
                
           #weaknesses
            if len(member.weaknesses) > 0:
                
                print(f"Your top weaknesses are: {member.weaknesses}")
                
                
                
                #options
                print("\nHere are 3 new problems to solve based on your weaknesses:")
                problems = member.fetch_practice_problem()
                
                if type(problems) == list: 
                    for i in problems:
                        print(i)
                else:
                    print(problems) # In case it returns the network error string
            else:
                print("You have no weaknesses. You are a professional coder, Good Job.")
                
            print("-" * 50)
    def export_to_csv(self, file_name):
        # 1. Stop if there is nothing to export
        if len(self.Members) == 0:
            print("No new members to export! Try adding someone first.")
            return

        # 2. Read the existing database into a dictionary
        all_data = {}
        try:
            with open(file_name, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    # If the row is not empty AND the first item is not our header word
                    if row and row[0] != "Handle":
                        all_data[row[0]] = row 
        except FileNotFoundError:
            pass

        # 3. Update the dictionary with our new members
        for member in self.Members:
            all_data[member.handle] = [
                member.handle,
                member.rank,
                member.rating,
                member.solve_count,
                member.weaknesses
            ]

        # 4. Write the clean data back to the file
        with open(file_name, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Handle", "Rank", "Rating", "Solve Count", "Weaknesses"])
            
            for handle in all_data:
                writer.writerow(all_data[handle])
                
        # Clear the memory 
        self.Members.clear() 
        print(f"Done! Check your folder for {file_name}.")
        
print("Initializing ScoutSystem...")
my_tracker = ScoutSystem("IT Team Tracker")

while True:
    print("\n" + "="*30)
    print("🏆 SCOUT SYSTEM MAIN MENU 🏆")
    print("="*30)
    print("1. Add a new member to track")
    print("2. Generate Master Coaching Report")
    print("3. Export data to CSV")
    print("4. Exit program")
    print("="*30)
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        handle = input("\nEnter Codeforces handle: ")
        print(f"Fetching data for {handle}...")
        my_tracker.add_member(handle)
        
    elif choice == "2":
        my_tracker.generate_report()
        
    elif choice == "3":
        print("\nExporting data...")
        my_tracker.export_to_csv("DataBase.csv")
        
        
    elif choice == "4":
        print("\nShutting down ScoutSystem. Goodbye!")
        break # This breaks the infinite loop and ends the program
        
    else:
        print("\nInvalid choice. Please type 1, 2, 3, or 4.")
