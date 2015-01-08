from generic import indicator_type
import datetime

def process(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('E') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data