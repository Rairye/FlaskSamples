import ResultGenerator
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
        return render_template("sent.html")

@app.route("/get_sentiment", methods=["POST"])
def get_sentiment ():
        single_dict = request.values.to_dict(flat=True)
        input_str = single_dict["input_str"]
        sent = ResultGenerator.get_sentiment(input_str)
        print("sentiment: " + sent)
        return jsonify({"sentiment" : sent})
                
if __name__ == "__main__":
        app.run(debug=True)
