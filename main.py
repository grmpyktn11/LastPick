import mysql.connector
import champions 
import databaseInfo
import helperFunctions
import requests
from bs4 import BeautifulSoup

db = mysql.connector.connect(
    host=databaseInfo.hostName,
    user=databaseInfo.databaseUsername,
    passwd=databaseInfo.databasePassword,
    database = databaseInfo.databaseName
)

cursor = db.cursor()
# cursor.execute("CREATE TABLE Player (name VARCHAR(50), champs VARCHAR(500),  playerID int PRIMARY KEY AUTO_INCREMENT)")

def insertPlayer(userName,champs):
    cursor.execute(f"INSERT INTO Player (name,champs) VALUES (%s,%s)", (userName, champs))
    db.commit()

def addUser():

    userNameTaken = True
    #loop for making sure that the username is not taken 
  
    
    while userNameTaken:
        nameInput = input("what is your name?")
        nameMatchQuery = "SELECT name FROM Player WHERE name = %s"
        cursor.execute(nameMatchQuery, (nameInput,))
        nameFound = cursor.fetchone()

        if nameFound is None:
            userNameTaken = False
        else:
            print("that name has been taken already, pick another ")
    

    amountOfChamps = helperFunctions.getValidInteger("The name is available. How many champs do you main? ")
    champPool = ''
    for i in range(amountOfChamps):
        championInput = input(f"enter champion #{i+1}").capitalize()

        while not (championInput in champions.championSet):
            championInput = input(f"not a champ, enter champion #{i+1} ")

        while(championInput in champPool):
            championInput = input("you already have that! enter another ")
        champPool += (f"{championInput},")

    champPool = champPool[:-1]
    insertPlayer(nameInput,champPool)
    print(f"Player successfully registered.\nname: {nameInput}\nchamps: {champPool}")

def getCounters(name, amount,lane):
        baseLink = "https://www.op.gg/champions/{}/counters/{}"
        url = baseLink.format(name.lower(),lane.lower())

        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            return None
        if(response.status_code == 200):
            soup = BeautifulSoup(response.content, 'html.parser')

            championDivs = soup.find_all('div', class_='css-72rvq0 ee0p1b94', limit=amount)
            counters = []
            for div in championDivs:
                counters.append(div.text.strip())
            countersString = ""
            for i in counters:
                countersString += (i +", ")
            countersString = countersString[:-2]
            return countersString
        else:
            print("failed to get the data website might be down")

    
def checkUser(user):
    nameMatchQuery = "SELECT name FROM Player WHERE name = %s"
    cursor.execute(nameMatchQuery, (user,))
    nameFound = cursor.fetchone()

    if nameFound is None:
        return(None)

    

    cursor.execute("SELECT champs FROM Player WHERE name = %s",(user,))
    userChamps = cursor.fetchone()
    userChamps = userChamps[0]
    return userChamps.split(',')
    
    

def playCounter(listOfChamps,opp,lane):
    tenCounters = getCounters(opp,10,lane)
    for i in listOfChamps:
        if i in tenCounters:
            return(f'since you main {i}, you should play them, they are in the top 10 counters for {opp} {lane}')
    return("looks like you dont play any of the top 10 counters")



if __name__ == "__main__":

    print("Welcome to LastPick!\nThis program aims to show you who to pick to counter your opponent's champ!")
    potentialResponses = ['login','logout','register','check','exit',"settings","TESTBASE"]
    login = False
    exited = False
    while(exited == False):
        response = input("What would you like to do: ""login"",""logout"", ""register"", ""check"", ""settings"" or ""exit?"" ")
        while not response in potentialResponses:
            response = input("Thats not a valid option, choose from the list above.")
        if(response == "TESTBASE"):
            cursor.execute("SELECT * FROM Player")
            for i in cursor:
                print(i)
        if(response == 'logout'):
            if(login == True):
                login = False
                credentials = None
                print("you have logged out")
            else:
                print("nobody is signed in")
        if(response == 'login'):
            if(login == False):
                username = input("what is your user?")
                credentials = checkUser(username)
                if(credentials is not None):
                    login = True
                    print("you have logged in!")
                else:
                    print("user not found, register or try again")
                
            else:
                print("you are already logged in")
        if(response == 'register'):
            addUser()
        
        if(response == 'check'):
            lanes = ["top",'mid','jungle','adc','support']
            lane = input("what lane are you playing")
            while lane not in lanes:
                lane = input("that is not a valid lane (top,mid,jungle,adc,support)")
            opp = input("Enter your opponent: ").capitalize()
            print(opp)
            while(opp not in champions.championSet):
                opp = input("thats not a valid champ broseph. Try again: ")
            print(f"the best counters for {opp} {lane} are {getCounters(opp,3,lane)}")
            if(login == True):
                print(playCounter(credentials, opp,lane))
            

        if(response == 'settings'):
            print('you are now in settings: this feature is still in development.')

        if(response == "exit"):
            exited = True
    print("Goodbye!")
    pass
