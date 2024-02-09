from auto_chatgpt import ChatGPTAutomation
from wiki_requests import fetch_content
from stories import ChromeCrawler
import json

def make_instructions(data, chatgpt, extra_tools=None, memories=None):
    instructions = []

    def collect_stories(**kwargs):
        output_from_chatgpt = kwargs['chatgpt_output']
        stories = {}
        for ref in output_from_chatgpt:
            ref_dict = extra_tools['ref_dict'][ref]
            stories[ref] = {'title': ref_dict['title'], 'url': ref_dict['url'], 'content': extra_tools['crawler'].get_articles(ref_dict['url']), 'source': ref_dict['publisher']}
        memories['stories'] = stories
        return stories
    
    def prompts_with_all_resources(data=None, memories=None, **kwargs):
        articles = []
        articles.append(f"data['title']\n{data['plain_text']}\n========\n")
        for story in memories['stories']:
            articles.append(f"{story['title']}\n{story['source']}\n{story['content']}\n========\n")
        prompt = "\n".join(articles)

        ideas = memories['ideas']

        prompt = f"{prompt}\nYou are a profesional writer for the gaming community. Now you plan to write a story about how the game was developed. Specifically, you want to focus on the following three ideas: {ideas}. You want to make sure that the story is engaging and informative. Now you need to draft a brief outline for the story!"
        return prompt
    
    instructions.append({
        "make_prompt": lambda **kwargs: f"{kwargs['data']['text_with_refs']}\n========\nI want to write a story about how the game was created. Could you give me 10 potential and intriguing ideas? Just list the title of your idea and a few setences (no more than three sentences) about it. Thanks!",
        "func_call": chatgpt.send_prompt_to_chatgpt
    })
    instructions.append({
        "prompt": "I hope readers find these ideas involving and interesting. This requires the ideas closely related to their game experience. Could you rate these ideas from 1 to 10 with your reasons? and choose the final 3 ideas to further elaborate on? Thanks!",
        "func_call": chatgpt.send_prompt_to_chatgpt
    })
    instructions.append({
        "prompt": "Generate a plain python dict containing these idea titles and descriptions, and output nothing else. Do not use code interpreter.",
        "func_call": chatgpt.send_prompt_to_chatgpt,
        "ending_funcs": lambda **kwargs: memories.update({'ideas': kwargs['chatgpt_output']})
    })
    instructions.append({
        "prompt": "Now, to start with these three ideas, do you need any references? There are inline references in the given article. Select the five relevant references you think are the most helpful to the story. Thanks! Generate a list containing the name of the references.",
        "func_call": chatgpt.restart_the_last_utterance
    })
    instructions.append({
        "prompt": "Generate a plain python list containing these names, and output nothing else. Do not use code interpreter.",
        "func_call": chatgpt.send_prompt_to_chatgpt,
        "ending_funcs": collect_stories
    })
    instructions.append({
        "starting_funcs": lambda **kwargs: chatgpt.new_session,
        "make_prompt": prompts_with_all_resources,
    })

    return instructions

if __name__ == "__main__":
    with open('parsed.json', 'r') as file:
        data = json.load(file)

    prompt = f"{data['text_with_refs']}\n========\nI want to write a story about how the game was created. Could you give me 10 potential and intriguing ideas? Just list the title of your idea and a few setences (no more than three sentences) about it. Thanks!"

    chrome_driver_path = '/Users/yucheng/.cache/selenium/chromedriver/mac-x64/121.0.6167.85/chromedriver'
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    # Create an instance
    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)
    crawler = ChromeCrawler()

    extra_tools={'crawler': crawler, 'ref_dict': data['ref_dict']}
    memories={}
    params = {'data': data, 'chatgpt': chatgpt, 'extra_tools': extra_tools, 'memories': memories}
    instructions = make_instructions(data, chatgpt, extra_tools=extra_tools, memories=memories)
    for instruction in instructions:
        if 'starting_funcs' in instruction:
            instruction['starting_funcs'](**params)

        if 'make_prompt' in instruction:
            prompt = instruction['make_prompt'](**params)
        else:
            assert 'prompt' in instruction, "Either make_prompt or prompt should be in the instruction"
            prompt = instruction['prompt']

        instruction['func_call'](prompt)
        memories.setdefault('conversation', []).append({'prompt': prompt})

        response = chatgpt.return_last_response()
        memories['conversation'][-1]['response'] = response

        if 'ending_funcs' in instruction:
            ending_params = {**params, 'chatgpt_output': chatgpt.return_last_response()}
            instruction['ending_funcs'](**params)

    # Save the conversation to a text file
    with open('conversation.json', 'w') as file:
        json.dump(memories['conversation'], file, indent=2, ensure_ascii=False)

    # Close the browser and terminate the WebDriver session
    chatgpt.quit()