import json

# loading my json file
with open('large_faqs.json', 'r') as file:
    faqs = json.load(file)

# initializing
context = ""

# create the data from that json file
for item in faqs:
    context += f"Question: {item['question']}\nAnswer: {item['answer']}\n\n"

# Save the context to a file in storedata.txt
with open('storedata.txt', 'w') as context_file:
    context_file.write(context)

print("Context has been saved to storedata.txt.")
