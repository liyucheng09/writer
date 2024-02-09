import requests
import traceback
import mwparserfromhell
import datetime
import os

import sys
import json
import time

from tqdm import tqdm

WIKI_API_ENDPOINT = "https://en.wikipedia.org/w/api.php"

def parse_to_plain_text(wikitext):
    parsed = mwparserfromhell.parse(wikitext)
    parsed_str = str(parsed)

    pure_text = parsed.strip_code()

    ref_dict = {}
    for tag in parsed.filter_tags(matches = "ref"):
        ref_name = tag.get('name').value.strip()
        if tag.contents.strip() == "":
            tag.contents = f"[Ref: {ref_name}]"
        else:
            citation = mwparserfromhell.parse(tag.contents).filter_templates()[0]
            ref_dict[ref_name] = {key.name.strip(): citation.get(key.name).value.strip() for key in reversed(citation.params)}
            tag.contents = ''
    for template in parsed.filter_templates(matches = 'Main'):
        main_ref = template.get(1).value.strip()
        main_label = main_ref.replace(' ', '_')
        main_link = 'https://en.wikipedia.org/wiki/' + main_label
        ref_dict[main_label] = main_link

        param_names = [i.name for i in reversed(template.params)]
        for param in param_names:
            template.remove(param)
        template.add('text', f"[Ref: {main_ref}]")
        
    text_with_refs = parsed.strip_code(keep_template_params=True)
    
    return {
        "plain_text": pure_text,
        "text_with_refs": text_with_refs,
        "parsed": parsed_str,
        "ref_dict": ref_dict
    }

def fetch_content(title, date=None):
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvlimit": "1",
    }
    if date: params["rvstart"] = date
    # try:
    response = requests.get(WIKI_API_ENDPOINT, params=params)
    response.raise_for_status()  # Will raise an error if the HTTP request returned an unsuccessful status code
    data = response.json()
    if 'error' in data:
        print(f"Error fetching content for {title}: {data['error']['info']}")
        return None

    page = next(iter(data['query']['pages'].values()))
    if 'revisions' not in page:
        print(f"No revisions found for {title}")
        return None
    content = page['revisions'][0]['*']
    
    # Check if the content is a redirect and skip if true
    if content.lower().startswith("#redirect"):
        print(f"{title} is a redirect page.")
        return None
    parsed = parse_to_plain_text(content)
    
    return parsed

    # except Exception as e:
    #     print(f"An error occurred while fetching content for {title}: {str(e)}")
    #     traceback.print_exc()  # This will print the full traceback

    # return None

if __name__ == "__main__":
    r = fetch_content('The_Last_of_Us')
    r['title'] = 'The Last of Us - Wikipedia'
    with open('parsed.json', 'w') as f:
        json.dump(r, f, indent=2, ensure_ascii=False)