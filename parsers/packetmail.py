from generic import indicator_type

def process(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition(';')[0].strip()
            date = line.split('; ')[1].split(' ')[0]
            data.append((i, indicator_type(i), direction, source, '', date))
    return data
