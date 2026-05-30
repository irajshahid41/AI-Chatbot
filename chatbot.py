from dotenv import load_dotenv
import os
from groq import (
    Groq,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIStatusError
)
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

print("Chatbot (Groq Streaming): Type 'quit', 'exit', 'bye' to stop\n")

while True:
    try:
        user_input = input("You: ")

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Goodbye!")
            break

        print("Chatbot: ", end="", flush=True)
      
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": user_input}
            ],
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

        print()

    except AuthenticationError:
        print("\n[ERROR] Invalid API key.")

    except RateLimitError:
        print("\n[ERROR] Rate limit exceeded. Please wait.")

    except APIConnectionError:
        print("\n[ERROR] Internet connection problem.")

    except APIStatusError as e:
        print(f"\n[ERROR] API Error: {e}")

    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
