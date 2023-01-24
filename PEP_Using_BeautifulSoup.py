# import libraries
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
url = 'https://www.af.mil/About-Us/Biographies/'

# Request to fetch the URL
response = urllib.request.urlopen(url)
soup = BeautifulSoup(response, 'html.parser', from_encoding=response.info().get_param('charset'))

print(f'fetch url: {url}')

tags = soup.select('p, h1, h2, h3, h4, h5, h6, strong, ul')

name = soup.find_all('h1')

print(name)

## Define the API key

# Define the openai function
def open_file(filepath):
    with open(filepath, 'r', encoding = 'utf-8') as infile:
        return infile.read()


openai.api_key = open_file('apikey/creds.txt')


## Create gpt3 function



def gpt3_completion(
    prompt,
    engine = 'text-davinci-003',
    temp = 0.7,
    top_p = 1.0,
    tokens = 900,
    freq_pen = 0.0,
    pres_pen = 0,
    stop = ['USER:', 'DARRYL']
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
            presence_penalty = pres_pen,
            stop = stop
        )

        text = response['choices'][0]['text'].strip()
        text = re.sub('\s+', ' ', text)
        filename = '%s_gpt3.txt' % time()

        with open('gpt3_logs/%s' % filename, 'w') as outfile:
            outfile.write('PROMPT:\n\n' + prompt + '\n\n=========\n\nRESPONSE:\n\n'+ text + '\n\n')


        return text
    except Exception as oops:
        retry += 1
        if retry >= max_retry:
            return 'GPT 3 error: %s' % oops
        print('Error communicating with OpenAI', oops)
        sleep()


## Define the definition of PEP
PEP_query = 'Definition of PEP (Politically Exposed Person).'

prompt = PEP_query
print(prompt)
res = gpt3_completion(prompt)

print(res)


## List the people from the name
name_query = f'List the name of the people from the following reading\n {name}'

prompt += prompt +'\n\n'+ res +'\n\n'+ name_query

print(prompt)
res = gpt3_completion(prompt)

print(res)

## Identify whether the person is a PEP or not

pep_or_not = 'Identify whether they are a Politically Exposed Person or not.'
print(prompt + '\n')
prompt += prompt + '\n' + res + '\n' + pep_or_not
res = gpt3_completion(prompt)
print(res)

## Provide with details of PEP person such as date of birth, country of residence, synopsis and position held
detail_query = 'Provide with the details of PEP people mention above (date of birth, position held, country of residence, and synopsis). Print it into CSV format.'


prompt = prompt + '\n' +res + '\n' +detail_query

print(prompt)

res = gpt3_completion(prompt)

print(res)
