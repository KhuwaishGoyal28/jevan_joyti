from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
import threading
import webbrowser

# Configure Google Generative AI with your API key
genai.configure(api_key="AIzaSyDJ8zqLWLSQnrSvIj-vgxRv-uBvfncxVa0")
model = genai.GenerativeModel("gemini-1.5-flash")

# HTML, CSS, and JS for the webpage
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Natural Disasters Information and Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #005f73;
            color: #fff;
            padding: 1rem;
            text-align: center;
        }
        main {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }
        .info, .chatbot {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            width: 100%;
            max-width: 600px;
            margin-bottom: 2rem;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #chat-output {
            height: 200px;
            width: 100%;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            overflow-y: auto;
            margin-bottom: 1rem;
            background-color: #f9f9f9;
        }
        #user-input {
            width: 80%;
            padding: 0.5rem;
        }
        button {
            padding: 0.5rem 1rem;
            background-color: #005f73;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <header>
        <h1>Natural Disasters Information</h1>
        <p>Get information and ask questions about various natural disasters.</p>
    </header>
    
    <main>
        <section class="info">
            <h2>Common Natural Disasters</h2>
            <ul>
                <li><strong>Earthquakes:</strong> Sudden shaking of the ground caused by tectonic activity.</li>
                <li><strong>Floods:</strong> Overflow of water submerging land, often due to heavy rainfall.</li>
                <li><strong>Hurricanes:</strong> Intense tropical storms with powerful winds and heavy rain.</li>
                <li><strong>Wildfires:</strong> Uncontrolled fires in forests or grasslands.</li>
            </ul>
        </section>

        <section class="chatbot">
            <h2>Chat with Our Bot</h2>
            <div class="chat-container">
                <div id="chat-output"></div>
                <input type="text" id="user-input" placeholder="Ask a question..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </section>
    </main>

    <script>
        async function sendMessage() {
            const userInput = document.getElementById("user-input").value;
            if (!userInput) return;

            // Display user's question
            const chatOutput = document.getElementById("chat-output");
            const userMessage = document.createElement("p");
            userMessage.textContent = "You: " + userInput;
            chatOutput.appendChild(userMessage);

            // Send question to the Flask backend
            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: userInput })
            });

            const data = await response.json();
            const botMessage = document.createElement("p");
            botMessage.textContent = "Bot: " + data.response;
            chatOutput.appendChild(botMessage);

            // Scroll to the bottom of chat output
            chatOutput.scrollTop = chatOutput.scrollHeight;

            // Clear the input field
            document.getElementById("user-input").value = "";
        }
    </script>
</body>
</html>
"""

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string(html_template)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")
    try:
        response = model.generate_content(user_input)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": "Error: Unable to connect to the chatbot service."})

# Run the Flask app in a separate thread
def run_app():
    app.run(port=5014, debug=False, use_reloader=False)

thread = threading.Thread(target=run_app)
thread.start()

# Open the web page in the default browser
webbrowser.open("http://127.0.0.1:5014")
