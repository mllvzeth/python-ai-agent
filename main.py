import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
import argparse
from prompts import system_prompt
from call_function import available_functions_tool, call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)


def main():
    print("Hello from python-ai-agent!")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    # Now we can access `args.user_prompt`

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    if args.verbose:
        print(f"User prompt: {messages}")

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0,
                    tools=[available_functions_tool],
                ),
            )

            if response.usage_metadata is None:
                raise RuntimeError("Usage data missing")
            if args.verbose:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(
                    f"Response tokens: {response.usage_metadata.candidates_token_count}"
                )

            func_calls = response.function_calls

            if func_calls is not None:
                for call in func_calls:
                    print(f"Calling function: {call.name}({call.args})")
                    function_call_result = call_function(call)
                    if not getattr(function_call_result, "parts", None):
                        raise ValueError(" Content.parts must be a non-empty list")

                    first_part = function_call_result.parts[0]

                    func_resp = getattr(first_part, "function_reponse", None)
                    if func_resp is None:
                        raise ValueError(
                            "Content.parts[0].function_response must not be None"
                        )

            else:
                print(f"Response: {response.text}")

            break
        except errors.ServerError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))  # simple backoff


if __name__ == "__main__":
    main()
