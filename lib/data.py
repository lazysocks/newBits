
import json, re

class Image:

    def __init__(self, json):
        self.json = self.get_json_data(json)
        self.data = self.find_model_keys(self.json)
        self.choice = self.get_choice(self.data)
        self.msg = print(self.print_device_info(self.choice))

    def get_json_data(self, file):
        with open(file, 'r') as read_file:
            data = json.load(read_file)
        return data
    
    def find_model_keys(self, data):
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

    def get_choice(self, choices):
        for k, v in choices.items():
            model = v['model']
            print(f'{k}: {model}')
        print('Select image by entering the device number ###: ')
        image_number = input()
        selected_device = choices.get(int(image_number))
        return selected_device
    
    def print_device_info(self, selected_device):
        msg = f'''
        You selected:
        Model: {selected_device['model']}
        Mfg: {selected_device['manufacturer']}
        Channel: {selected_device['channel']}
        Pattern: {selected_device['hwidmatch']}
        Chrome Version: {selected_device['chrome_version']}
        Build Version: {selected_device['version']}
        '''
        return msg


    