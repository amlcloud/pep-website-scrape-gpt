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


## define the URL

# Provide with the URL
url = 'https://www.aph.gov.au/Senators_and_Members/Parliamentarian_Search_Results?q=&mem=1&par=-1&gen=0&ps=0'

# Request to fetch the URL
response = urllib.request.urlopen(url)

# Define the Beautiful Soup
soup = BeautifulSoup(response, 'html.parser', from_encoding=response.info().get_param('charset'))

# Print to show the url has been fetch
print(f'fetch url: {url}{response}')

# Instead of this tag
tags = soup.select('p, h1, h2, h3, h4, h5, h6, strong, ul')

# I would like to get to know the length of tags for the reference
print(f'Lengths of tags: {len(tags)}')


## Define the API key

# Define the openai function
def open_file(filepath):
    with open(filepath, 'r', encoding = 'utf-8') as infile:
        return infile.read()

# Give access to API so I can use it
openai.api_key = open_file('apikey/creds.txt')


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


# Define the definition  of PEP
PEP_query = 'Please tell me the definition of PEP (Politically Exposed Person).'

# Define the prompt
prompt = PEP_query


#Print the prompt
print(PEP_query)

# Input the prompt into gpt3 completion
res = f'{gpt3_completion(prompt)}'

# Print the response
print(res)


## List the people from the name
# For the tags[30:-30], I narrowed down the length as it is going to exceed the max tokens if I print the full length
name_query = f'{tags[30:-30]}\nFrom the reading above, list the people from above and occupation in the format of people, occupation.'

# It concatinate the prompt with pervious response as openai assumes that you only ask one question
prompt = f"{res}\n{name_query}"

# Print the name query prompt
print(name_query)

# Input the prompt into GPT3 Completion
res = gpt3_completion(prompt)

# print the response
print(res)

## Identify whether the person is a PEP or not

pep_or_not = 'Identify whether they are a PEP (Politically Exposed Person or not).'

# Concatinate the prompt as the openai only assume that you only ask one question
prompt += f"\n{res} \n {pep_or_not}\n"

# Print the pep_or_not prompt
print(pep_or_not)

# Input the prompt into openai gpt3 function
res = gpt3_completion(prompt)

# Print the response
print(res)

## Provide with details of PEP person such as date of birth, country of residence, synopsis and position held
detail_query = 'Please give me the first name, last name, date of birth, country of residence, synopsis, and position held of the people who are a PEP in the format of first name last name, DateOfBirth, CountryOfResidence, Synopsis, PositionHeld. Print it in a CSV file.'

# It concatinate the prompt with pervious response as openai assumes that you only ask one question
prompt += f"\n {res}  \n {detail_query}\n"

# Print the prompt of detail query
print(detail_query)

# Input the prompt into GPT3 Completion
res = gpt3_completion(prompt)

# Print the response
print(res)
