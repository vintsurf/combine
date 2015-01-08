from generic import indicator_type

def process(response, source, direction):
    data = []
    if response.startswith("Couldn't select database"):
        return data
    for line in response.splitlines():
        if not line.startswith('S') and len(line) > 0:
            i = line.partition(',')[0].strip()
            date = line.split(',')[1].split()[0]
            note = line.split(',')[-1]
            data.append((i, indicator_type(i), direction, source, note, date))
    return data
