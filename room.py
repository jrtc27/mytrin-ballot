import decimal
import json
import os
import urllib
import shutil

class Room(object):
    def __init__(self, data):
        if isinstance(data, list):
            name = data[0].text
            charge = data[1].text
            room_type = data[2].text
            ensuite = data[3].text
            bath = data[4].text
            shower = data[5].text
            gyp = data[6].text
            sink = data[7].text
            name_split = name.split(' ')

            self.court = ' '.join(name_split[:-1])
            self.staircase = name_split[-1][0]
            self.number = name_split[-1][1:]
            self.charge = decimal.Decimal(charge)
            self.room_type = room_type
            self.ensuite = self._bool_from_cell(ensuite, 'Ensuite')
            self.bath = self._bool_from_cell(bath, 'Bath')
            self.shower = self._bool_from_cell(shower, 'Shower')
            self.gyp = self._bool_from_cell(gyp, 'Gyp')
            self.sink = self._bool_from_cell(sink, 'Sink')
            self.url = 'https://my.trin.cam.ac.uk/accom/' + urllib.parse.quote(name.replace('\'', '')) + '.pdf'
        elif isinstance(data, dict):
            self.court = data['court']
            self.staircase = data['staircase']
            self.number = data['number']
            self.charge = data['charge']
            self.room_type = data['room_type']
            self.ensuite = data['ensuite']
            self.bath = data['bath']
            self.shower = data['shower']
            self.gyp = data['gyp']
            self.sink = data['sink']
            self.url = data['url']
        else:
            raise Exception("Invalid argument type: {}".format(type(data)))

        assert self.room_type in { 'Bed Sit', 'Double', 'Set' }

    def get_pdf_path(self):
        directory = os.path.join(self.court, self.staircase)
        return os.path.join(directory, self.get_pdf_filename())

    def get_pdf_filename(self):
        return self.court + ' ' + self.staircase + self.number + '.pdf'

    def download_to_file(self, directory='PDFs'):
        path = os.path.join(directory, self.get_pdf_path())
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with urllib.request.urlopen(self.url) as response, open(path, 'wb') as f:
            shutil.copyfileobj(response, f)

    @staticmethod
    def _bool_from_cell(value, true, false=''):
        if value == true:
            return True
        if value == false:
            return False
        raise Exception('\'{}\' is neither \'{}\' nor \'{}\''.format(value, true, false))

    def __str__(self):
        s = '{} {}{} ({}) @ {}'.format(self.court, self.staircase, self.number, self.room_type, self.charge)
        components = [s]
        if self.ensuite:
            components.append('Ensuite')
        if self.bath:
            components.append('Bath')
        if self.shower:
            components.append('Shower')
        if self.gyp:
            components.append('Gyp')
        if self.sink:
            components.append('Sink')
        return ', '.join(components)

    def __json__(self):
        return {
            'court': self.court,
            'staircase': self.staircase,
            'number': self.number,
            'charge': self.charge,
            'room_type': self.room_type,
            'ensuite': self.ensuite,
            'bath': self.bath,
            'shower': self.shower,
            'gyp': self.gyp,
            'sink': self.sink,
            'url': self.url
        }

    def __repr__(self):
        return str(self.__json__())

class SmartJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        elif isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)

def load_from_json(path='rooms.json'):
    with open(path, 'r') as f:
        return list(map(Room, json.load(f, parse_float=decimal.Decimal)))

def save_to_json(rooms, path='rooms.json'):
    with open(path, 'w') as f:
        json.dump(rooms, f, cls=SmartJSONEncoder, sort_keys=True, indent=4)
