import databaseInfo
import mysql.connector
import champions
import requests
from bs4 import BeautifulSoup

db = mysql.connector.connect(

    host=databaseInfo.hostName,
    user=databaseInfo.databaseUsername,
    passwd=databaseInfo.databasePassword,
    database = databaseInfo.databaseName
)

cursor = db.cursor()

def checkDb():
    cursor.execute("SELECT * FROM Player")
    for i in cursor:
        print(i)


def verifyUser(user):
    nameMatchQuery = "SELECT name FROM Player WHERE name = %s"
    cursor.execute(nameMatchQuery, (user,))
    nameFound = cursor.fetchone()
    if nameFound is None:
        return False
    else:
        return True
    
def addUser(name, pool):
    if(not name):
        return "You did not include a name!"
    champPool = pool.split(",")
    for i in champPool:
        if(i.capitalize() not in champions.championSet):
            return("One of your champs is not a valid champ")
    if (verifyUser(name)):
        return("Username has been taken.")
    cursor.execute(f"INSERT INTO Player (name,champs) VALUES (%s,%s)", (name, pool))
    db.commit
    return("User has been successfully registered, please log in.")

    
# def getValidInteger(prompt):
#     while True:
#         try:
#             value = int(input(prompt))
#             return value
#         except ValueError:
#             print("Please enter a valid integer.")


def getCounters(opp, amount,lane):
        if opp.capitalize() not in champions.championSet:
            return "please input a valid champ."
        lanes = {"Top","Mid","Jungle","Adc","Support"}
        if lane.capitalize() not in lanes:
            return "please input a valid lane"
        baseLink = "https://www.op.gg/champions/{}/counters/{}"
        url = baseLink.format(opp.lower(),lane.lower())

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
            return("failed to get the data website might be down")


def playsCounter(user,opp, lane):
    cursor.execute(f"SELECT champs FROM Player WHERE name = %s",(user,))
    
    oppsCounters = getCounters(opp, 10, lane)
    userChamps = cursor.fetchone()[0].split(',')
    
    for i in userChamps:
        if i in oppsCounters:
            return (f"You should play {i}, they are one of your mains and in the top 10 counters for {opp}")
    return ("you dont main any of the top 10 counters, try a new champ!")
