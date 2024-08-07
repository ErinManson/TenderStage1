import os
import openai
import json
import time

# Set your OpenAI API key
api_key = "API_KEY"
openai.api_key = api_key

def process_file(file_path, file_id, output_directory):
    with open(file_path) as f:
        file_text = f.read().strip()

    prompt = f"""Fill out the empty JSON template using the text below. Use true/false answers when possible.\n{file_text}
    {{
        "solicitation closes": {{
          "date": {{}},
          "time": {{}}
        }},
        "details": {{
          "type": {{}},
          "quantity": {{}}
        }},
        "criteria": {{
          "environmental": {{
            "recyclable materials": {{}},
            "ANSI/BIFMA e3 minimum Level® 2": {{}}
          }},
          "weight capacity": {{
            "standard": {{}},
            "large-occupant": {{}}
          }},
          "usage": {{
            "single shift": {{}},
            "24/7": {{}}
          }},
          "headrest": {{
            "no": {{}},
            "yes": {{}},
            "no preference": {{}}
          }},
          "backrest": {{
            "standard": {{}},
            "high": {{}},
            "no preference": {{}}
          }},
          "lumbar support": {{
            "fixed position": {{}},
            "adjustable (by user)": {{}},
            "self-adjusting mechanism": {{}},
            "no preference": {{}}
          }},
          "armrests": {{
            "adjustable": {{
                "height adjustment": {{}},
                "lateral adjustment": {{}},
                "fully articulating": {{}},
                "cushioned": {{}},
                "t-arm": {{}},
                "cantilever": {{}}
            }},
            "fixed": {{
                "t-arm": {{}},
                "cantilever": {{}}
            }},
            "casters": {{
                "loop": {{}},
                "no preference": {{}}
            }}
          }},
          "seat depth": {{
            "adjustable": {{}},
            "fixed": {{
                "shallow": {{}},
                "medium": {{}},
                "deep": {{}}
            }}
          }},
          "seat width": {{}},
          "seat height": {{
            "adjustable-standard range": {{}},
            "adjustable-low range": {{}},
            "adjustable": {{}}
          }},
          "tilt mechanism": {{
            "multifunction": {{}},
            "synchro tilt": {{}},
            "unison tilt": {{}},
            "fixed back": {{}},
            "no preference": {{}}
          }},
          "casters": {{
            "carpet": {{}},
            "hard surfaces": {{}}
          }},
          "footrest (rotary stool only)": {{
            "integrated fixed height": {{}},
            "adjustable height": {{}}
          }},
          "finishes": {{
            "backrest": {{
                "upholstery": {{}},
                "non-upholstery (i.e., flexible plastic)": {{}},
                "mesh material": {{}}
            }},
            "seat": {{
                "upholstery": {{}},
                "non-upholstery (i.e., flexible plastic)": {{}},
                "mesh material": {{}}
            }},
            "base frame": {{
                "metal": {{}},
                "plastic": {{}}
            }}
          }},
          "labeling and instructions": {{
            "chairs must be provided with labeling and instructions": {{}}
          }},
          "accessibility": {{
            "not applicable": {{}},
            "adjustment levers to be equipped with braille": {{}}
          }}
        }},
        "additional criteria": {{}}
    }}"""

    for attempt in range(4):  # Try up to 4 times
        try:
            # Requesting completion with the gpt-3.5-turbo chat model
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000  # Adjust max_tokens as needed
            )

            # Parse the completed JSON response
            completed_json = response['choices'][0]['message']['content'].strip()
            completed_dict = json.loads(completed_json)

            # Create the output JSON file with the same name as the input text file
            output_file_path = os.path.join(output_directory, f"{file_id}.json")
            with open(output_file_path, 'w') as json_file:
                json.dump(completed_dict, json_file, indent=2)

            print(f"Processed {file_path} -> {output_file_path}")
            return True  # Exit the function if successful

        except json.JSONDecodeError:
            print(f"Error decoding JSON response for file: {file_path}, attempt {attempt + 1}")
            if attempt < 3:  # Wait only if it's not the last attempt
                time.sleep(1)  # Wait for a second before retrying

    return False  # Return False if all attempts fail

def main():
    input_directory = r"Posts"
    output_directory = r"JSONS"
    os.makedirs(output_directory, exist_ok=True)

    # Iterate over files in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            file_id = filename.split('.')[0]  # Extract the id from the filename
            file_path = os.path.join(input_directory, filename)
            if not process_file(file_path, file_id, output_directory):
                print(f"Failed to process {file_path} after 4 attempts")

if __name__ == "__main__":
    main()
