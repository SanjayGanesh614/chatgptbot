from flask import Flask, render_template, request, Response, stream_with_context
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():
    global conversation_history
    user_msg = request.json['message']
    conversation_history.append({"role": "user", "content": user_msg})

    def generate():
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history,
            stream=True
        )
        full_response = ""
        for chunk in response:
            if 'choices' in chunk:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    content = delta['content']
                    full_response += content
                    yield f"data: {content}\n\n"
        conversation_history.append({"role": "assistant", "content": full_response})

    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
