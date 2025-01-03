import openai

# Set your OpenAI API Key
openai.api_key = "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"

# Define a test input text
test_input = "I was always warned to learn code but never learn code properly and facing difficulty in software jobs getting."

# Function to enhance text using OpenAI
def enhance_text_with_openai(input_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases text in a formal, concise, and coherent manner."},
                {"role": "user", "content": f"Rephrase the following text:\n\n{input_text}"}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        enhanced_text = response['choices'][0]['message']['content'].strip()
        return enhanced_text
    except openai.error.InvalidRequestError as e:
        return f"Invalid request error: {str(e)}"
    except openai.error.AuthenticationError as e:
        return f"Authentication error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Call the function with the test input
enhanced_output = enhance_text_with_openai(test_input)

# Print the output
print("Enhanced Text Output:")
print(enhanced_output)
