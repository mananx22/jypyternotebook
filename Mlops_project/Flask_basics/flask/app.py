from flask import Flask

app=Flask(__name__)

@app.route("/")
def welcome():
    return "welcome to first flask app, Hi"

if __name__=="__main__":
    app.run(debug=True)