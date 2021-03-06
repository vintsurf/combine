from yapsy.IPlugin import IPlugin
import datetime

class PluginOne(IPlugin):
    NAME = "arbormap"
    DIRECTION = "inbound"
    URLS = ['http://www.gstatic.com/ddos-viz/attacks.json']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        data = []
        current_date = str(datetime.date.today())
        for line in response.splitlines():   
           if 'subclass' in source:
               i = line.split()[0]
    	       data.append({'indicator':i, 'indicator_type':i['subclass'], 'indicator_direction':'inbound'})
	return data
