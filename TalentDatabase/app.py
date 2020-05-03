from flask import Flask, render_template, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

app = Flask (__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///talent_pool"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "key"
engine = create_engine("sqlite:///talent_pool", connect_args={"check_same_thread": False}, poolclass=StaticPool)
engine.connect()

db = SQLAlchemy(app)

strip_punct(word):
    return word.translate(str.maketrans('', '', "\"\';"))

class Talent(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(500))
    skills = db.Column("skills", db.String(1000))
    notes = db.Column("notes", db.String(1000))

    def __init__(self, name, skills, notes):
        self.name = name
        self.skills = skills
        self.notes = notes
        
@app.route("/add_talent", methods=["POST"])
def add_talent():
    single_dict = request.values.to_dict(flat=True)
    name = strip_punct(single_dict["name"])
    skills = strip_punct(single_dict["skills"])
    notes = strip_punct(single_dict["notes"])

    new_talent = None
    response = "Success"
    try:
        new_talent = Talent(name, skills, notes)
        db.session.add(new_talent)
        db.session.commit()
    except:
        response = "There was an error adding the new talent."
    
    return jsonify({"response" : response})

@app.route("/search_talent", methods=["POST"])
def search_talent():

    name = strip_punct(request.form.get("name"))
    skills = strip_punct(request.form.get("skills"))
    notes = strip_punct(request.form.get("notes"))

    search_statement = "SELECT * FROM talent" if name == "" and (skills == "" and notes == "") else "SELECT * FROM talent WHERE"

    if name != "":
        search_statement += " name LIKE " + ("'%{}%'" if skills == "" and notes == "" else "'%{}%' AND").format(name, name)
    if skills != "":
        search_statement += " skills LIKE " + ("'%{}%'" if notes == "" else "'%{}%' AND").format(skills, skills)
    if notes != "":
        search_statement += " notes LIKE '%{}%'".format(notes)

    search_statement += " ORDER BY name;"

    results = None
    try:
        results = engine.execute(search_statement)
    except:
        flash("There was an error reading from the database. Please try again.")
        return

    results_table = ""
    i = 0

    for result in results.fetchall():

        result_div = "<hr name ='table_hr'>"
        
        result_div += "<div name='result_div'><text name = 'result_text_heading'>Result {}</text><br><br>".format(i + 1)
        
        result_div += "<text name ='result_text_heading'>Name: </text><text name='result_text_body'>" + result[1] + "</text><br><br>"

        result_div += "<text name ='result_text_heading'>Skills: </text><text name = 'result_text_body'>" + (result[2] if result[2] != None else "") + "</text><br><br>"
        
        result_div += "<text name ='result_text_heading'>Notes: </text><text name = 'result_text_body'>" + (result[3] if result[3] != None else "") + "</text><br><br>"                 

        result_div += "<a href = '/update/{}'><text name = 'result_text_body'>Update information</text></a><br><br></div>".format(result[0])

        results_table += result_div

        i+=1

    if i == 0:
        results_table = "<text name ='result_text_title'>0 matches found.</text>"

    elif i == 1:
        results_table = "<text name = 'result_text_title'>1 match found.</text><br><br>" + results_table

    else:
        results_table = "<text name = 'result_text_title'>{} matches found.</text><br><br>".format(i) + results_table

    return render_template("results.html", results = results_table)

@app.route("/update_talent", methods=["POST"])
def update_talent():
    single_dict = request.values.to_dict(flat=True)
    id_number = single_dict["id"]
    name = strip_punct(single_dict["name"])
    skills = strip_punct(single_dict["skills"])
    notes = strip_punct(single_dict["notes"])
    response = "Success"
    
    try:
        engine.execute("UPDATE talent SET name = '{}', skills = '{}', notes = '{}' WHERE id = {};".format(name, skills, notes, id_number))
        db.session.commit()    
    except:
        response = "The talent could not be updated." 
                      
    return jsonify({"response" : response})

@app.route("/delete_talent", methods=["POST"])
def delete_talent():
    single_dict = request.values.to_dict(flat=True)
    id_number = single_dict["id"]
    response = "Success"
    
    try:
        engine.execute("DELETE FROM talent WHERE id = {};".format(id_number))
        db.session.commit()    
    except:
        response = "The talent could not be deleted."
                      
    return jsonify({"response" : response})

@app.route("/")
def home():
    session["user"] = "user"
    return render_template("index.html")

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/search")
def search ():
    return render_template("search.html")

@app.route("/update/<int:id_num>", methods=["GET"])
def update(id_num):
    
    talent = []
    try:
        results = (engine.execute("SELECT * FROM talent WHERE id = {};".format(id_num)))
        for result in results.fetchall():
            talent.append(result[0])
            talent.append(result[1] if result[1] != None  else "")
            talent.append(result[2] if result[2] != None else "")
            talent.append(result[3] if result[3] != None else "")
    except:
        return "The record could not be loaded. Please try again."

    return render_template("update.html", talent = talent)

if __name__ == "__main__":
    db.create_all()
    app.run()
