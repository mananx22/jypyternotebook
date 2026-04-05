from flask import Flask,render_template,request

app=Flask(__name__)

@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/form", methods=['GET','POST'] )
def form():
    if request.method == 'POST':
        name = request.form['name']
        return f" Welcome {name}, how are you"
    else:
        return render_template("form.html")
    
## jinja .py
# 1) variable rule 
@app.route("/success/<int:score>")
def success(score):
    res = ""
    if score > 50:
        res = "Passed"
    else:
        res = "failed"

    return render_template('results.html', results=res, scr=score)

# 2) variable rule with loop 
@app.route("/successloop/<int:score>")
def successloop(score):
    res = ""
    if score > 50:
        res = "Passed"
    else:
        res = "failed"
    exp = {"res":res,"score":score}
    return render_template("./loop_result.html", expression=exp)

# 3) conditions  with variables 
@app.route("/successif/<int:score>")
def successif(score):    
    return render_template("./if_result.html",score=score)


if __name__=="__main__":
    app.run(debug=True)