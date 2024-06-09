from flask import Flask, render_template, session, request, redirect, url_for, flash
import databaseInfo
import helperFunctions
import mysql.connector




app = Flask(__name__)
app.secret_key = databaseInfo.appSecretKey

loggedInStatus = False #global variable to track login
failedLogin = False

@app.route("/") # home page
def home():
    return render_template("index.html")

@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        registeredUsername = request.form["registrationName"]
        registeredChampionPool = request.form["listOfChampions"]
        session["regUser"] = registeredUsername
        session["regPool"] = registeredChampionPool
        registrationStatus = helperFunctions.addUser(registeredUsername, registeredChampionPool)
        registrationStatusString = registrationStatus
        print(registrationStatusString)
        session.pop("regUser", None)
        session.pop("regPool", None)
        return render_template("register.html", registrationStatusStatement = registrationStatusString)

    return render_template("register.html", registrationStatusStatement = "Register here!")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        session["user"] = user
        
        if helperFunctions.verifyUser(user):
            return redirect(url_for("check", usr = user))
        else:
            return render_template("login.html", loggedIn = False, failedLogin = True)

    else:
        return render_template("login.html", loggedIn = loggedInStatus, failedLogin = False)
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    loggedIn = False
    flash("you have been logged out")
    return redirect(url_for("check"))



@app.route("/check", methods=["GET","POST"])
def check():
    checkCalled = False
    counterMatch = ""    
    customCounter = ""

    if (not session.get("user")):
        loginStatus = "You are not logged in."
    else:
        loginStatus = f'you are logged in as {session.get("user")}'
    if(request.method == "POST"):
        checkCalled = True
        enemy = request.form["opponent"]
        lane = request.form["lane"]

        topCounters = helperFunctions.getCounters(enemy,3,lane)
        if(loggedInStatus == True):
            playerPlaysCounter = helperFunctions.playsCounter(session["user"],enemy,lane)
        else:
            playerPlaysCounter = "Login/register to get personalized recs!"
        
        counterMatch = topCounters  # Assign counters to variable
        customCounter = playerPlaysCounter

        return render_template("check.html",loginStatus = loginStatus, checkCalled = checkCalled, counterMatch = topCounters, customCounter = playerPlaysCounter)
    
    return render_template("check.html", loginDisplay = loginStatus)

    



if __name__ == "__main__":
    app.run(debug=True)