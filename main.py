from auto_chatgpt import ChatGPTAutomation
from wiki_requests import fetch_content
import json

if __name__ == "__main__":
    with open('parsed.json', 'r') as file:
        data = json.load(file)

    prompt = f"{data['text_with_refs']}\n========\nI want to write a story about how the game was created. Could you give me 10 potential and intriguing ideas? Just list the title of your idea and a few setences (no more than three sentences) about it. Thanks!"

    chrome_driver_path = '/Users/yucheng/.cache/selenium/chromedriver/mac-x64/121.0.6167.85/chromedriver'
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    # Create an instance
    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

    # Define a prompt and send it to chatgpt
    chatgpt.send_prompt_to_chatgpt(prompt)

    # Retrieve the last response from ChatGPT
    response = chatgpt.return_last_response()
    print(response)

    round2_prompt = "I hope readers find these ideas involving and interesting. This requires the ideas closely related to their game experience. Could you rate these ideas from 1 to 10 with your reasons? and choose the final 3 ideas to further elaborate on? Thanks!"
    chatgpt.send_prompt_to_chatgpt(round2_prompt)
    response = chatgpt.return_last_response()
    print(response)

    round3_prompt = "Now, to start with these three ideas, do you need any references? There are inline references in the given article. Select the five relevant references you think are the most helpful to the story. Thanks! Generate a list containing the name of the references."
    chatgpt.send_prompt_to_chatgpt(round3_prompt)
    response = chatgpt.return_last_response()
    print(response)

    # Save the conversation to a text file
    file_name = "conversation.txt"
    chatgpt.save_conversation(file_name)

    # Close the browser and terminate the WebDriver session
    chatgpt.quit()