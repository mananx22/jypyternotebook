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
    return "you have received" + str(score)


if __name__=="__main__":
    app.run(debug=True)