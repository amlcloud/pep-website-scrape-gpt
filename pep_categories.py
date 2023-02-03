## import libraries
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup


import os
import openai

from time import time, sleep


import io
import json

import regex as re

from dotenv import load_dotenv

# Load the environment
load_dotenv()

# Get the API KEY
API_KEY = os.getenv("API_KEY")

# I print the API Key just to test whether I can still load the API KEY
# print(f'API Key:{API_KEY}')

openai.api_key = API_KEY

## Create gpt3 function
def gpt3_completion(
    prompt,
    engine = 'text-davinci-003',
    temp = 0.10,
    top_p = 1.0,
    tokens = 900,
    freq_pen = 0.0,
    pres_pen = 0
):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding = 'ASCII', errors = 'ignore').decode()

    try:
        response = openai.Completion.create(
            engine = engine,
            prompt = prompt,
            temperature = temp,
            max_tokens = tokens,
            top_p = top_p,
            frequency_penalty = freq_pen,
            presence_penalty = pres_pen
        )

        text = response['choices'][0]['text'].strip() # print the text only
        text = re.sub('\s+', ' ', text) # replace the white space with ' '
        filename = '%s_gpt3.txt' % time()

        with open('gpt3_logs/%s' % filename, 'w') as outfile:
            outfile.write('PROMPT:\n\n' + prompt + '\n\n=========\n\nRESPONSE:\n\n'+ text + '\n\n')


        return text
    except Exception as oops:
        retry += 1
        if retry >= max_retry:
            return 'GPT 3 error: %s' % oops
        print('Error communicating with OpenAI', oops)


# Create the split function
def split(string, delimiter):
    li = list(string.split(delimiter))
    return li

# Provide wiht the URL
url = 'https://www.unicef.org/media/experts'

# Request to fetch the URL
fetch = urllib.request.urlopen(url)

# Define the Beautiful Soup
soup = BeautifulSoup(fetch, 'html.parser', from_encoding = fetch.info().get_param('charset'))

# Print to show the url has been fetch
print(f'fetch url: {url}{fetch}')

# Define the tag
tags = soup.select('p, h1, h2, h3, h4, h5, h6, strong, ul, li')

# I would like to get to know the length of tags for the reference
print(f'Lengths of tags: {len(tags)}')


# Shorten the length tags as I would not want to exceed maximum token
tags = tags[150:-80]
# print(tags)

# Define the prompt
query = f'{tags}\nPlease list name and of the people along from the reading above. Print the information in the format of firstname lastname: occupation. Print the information in semicolon format'

# Generate the gpt3
people = f'{gpt3_completion(query)}'

# Split the string into list
names = split(people, ';')

# Adding Serge Ivo and Joe Biden
names.append('Serge Ivo')
names.append('Joe Biden')

# Print the string
print(names)

# Initialise the query
pep_queries_0 = 'Definition of PEP'
pep_queries_1 = ['What do you know about the person named {0} who is currently working for UNICEF? Provide with date of birth and nationality as well. Print it with the semicolon separator in the format of Name;DateofBirth;Nationality;PositionHeld;background.'.format(name) for name in names]
pep_queries_2 = '\nFrom the reading above, print the information in the '
pep_queries_3 = 'Print the information into CSV in the semicolon format and the format of name,dateofbirth, nationality, position held'

# Define the empty data
data = []

for index, query in enumerate(pep_queries_1):
    
    response = openai.Completion.create(
        model = 'text-davinci-003',
        prompt = query,
        temperature = 0.0,
        max_tokens = 400,
        top_p = 1.0,
        frequency_penalty = 0.0,
        presence_penalty = 0.0
        
    
    )
    _response = response.choices[0]['text']
    data.append(_response)
    # data += f'{_response}\n'
    print(_response )


print(data)