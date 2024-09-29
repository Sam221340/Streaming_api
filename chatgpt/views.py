import json
from django.utils import timezone

import requests
from django.shortcuts import render, redirect

# Create your views here.
from django.http import StreamingHttpResponse, JsonResponse, request
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)


# views.py

@csrf_exempt
def stream_completions(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    elif request.method == 'POST':
        user = request.user
        print(user, "User")
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
        if user_message:
            # Retrieve the list of messages from the session or create an empty list if it doesn't exist
            messages = request.session.get('messages', [])
            messages.append(user_message)
            request.session['messages'] = messages
            if 'session_creation_time' not in request.session:
                request.session['session_creation_time'] = timezone.now().isoformat()

            messages = [{"role": "user", "content": user_message}]
            response = client.chat.completions.create(
                messages=messages,
                model="openai/gpt-3.5-turbo",
                stream=True
            )

            # Define a generator function to yield JSON responses
            def generate_json_response():
                list1 = []
                for chunk in response:
                    if chunk.choices:
                        for choice in chunk.choices:
                            completion = choice.delta.content
                            list1.append(completion)
                            # Yield each completion as a JSON response
                            yield json.dumps({'completion': completion}) + '\n'

                # signal that response has fully generated
                response_1 = request.session.get('response_1', [])
                response_1.append(clean_up_list(list1))
                request.session['response_1'] = response_1
                print(request.session.get('response_1'), "RESPONSE_1")

                session_data = request.session
                for key, value in session_data.items():
                    print(f"-------{key}:------------ {value}")
                yield json.dumps({'completion': '__END_OF_RESPONSES__'}) + '\n'

            # Return a streaming HTTP response with the generated JSON responses
            return StreamingHttpResponse(generate_json_response(), content_type='application/json')
        else:
            return JsonResponse({'error': 'Empty message'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def clean_up_list(list_to_clean):
    # Join the list elements into a single string
    text = ' '.join(list_to_clean)

    # Remove unnecessary spaces
    text = ' '.join(text.split())

    sentences = text.split('. ')
    cleaned_text = '. '.join(sentence.strip().capitalize() for sentence in sentences)

    return cleaned_text


def show_completions(request):
    user_message = request.session.get('messages')
    print(user_message, "mesage here")

    session_created = request.session.get('session_creation_time')
    answer = request.session.get('response_1')
    print(answer, "ANSWER")
    return render(request, 'session_data.html',
                  {'user_message': user_message, 'session': session_created, 'answer': answer})


def end_session(request):
    request.session.clear()
    return redirect('stream')
