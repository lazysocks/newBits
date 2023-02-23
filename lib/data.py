
import json, re

#Convert JSON data into dictionary
def get_json_data(file):
    with open(file, 'r') as read_file:
        data = json.load(read_file)
    return data

def find_model_keys(data):
    choices = {}
    result = None
    hwid_string = input('If you know the Model string displayed at the recovery screen,\n type some or all of it; otherwise just press Enter: ')
    hwid_pattern = hwid_string.upper()[0:9]
    if hwid_pattern:
        for i, model in enumerate(data):
            if model['channel'] == 'STABLE' and re.search(hwid_pattern, model['hwidmatch']):
                choices[i] = model
    else:
        for i, model in enumerate(data):
            if model['channel'] == 'STABLE':
                choices[i] = model
    return choices

def get_choice(choices):
    for k, v in choices.items():
        model = v['model']
        print(f'{k}: {model}')
    print('Select image by enteriong the image number ###: ')
    image_number = input()
    selected_device = choices.get(int(image_number))
    return selected_device
