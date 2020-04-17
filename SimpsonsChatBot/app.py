import ChatBot
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
        return render_template("bot.html")

@app.route("/chat", methods=["GET"])
def chat ():
        string = request.args.get("input_str")
        chat_response = ChatBot.get_response(string)
        return jsonify({"chat_response" : chat_response})
                
if __name__ == "__main__":
        app.run(debug=True)
