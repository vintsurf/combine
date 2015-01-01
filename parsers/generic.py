import csv
import requests
import re
import datetime
import grequests
import time
import StringIO

def process_simple_list(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data

def indicator_type(indicator):
    ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    domain_regex = '(www\.)?(?P<address>([\d\w.][-\d\w.]{0,253}[\d\w.]+\.)+(AC|AD|AE|AERO|AF|AG|AI|AL|AM|AN|AO|AQ|AR|ARPA|AS|ASIA|AT|AU|AW|AX|AZ|BA|BB|BD|BE|BF|BG|BH|BI|BIZ|BJ|BM|BN|BO|BR|BS|BT|BV|BW|BY|BZ|CA|CAT|CC|CD|CF|CG|CH|CI|CK|CL|CM|CN|COM|COOP|CR|CU|CV|CX|CY|CZ|DE|DJ|DK|DM|DO|DZ|EC|EDU|EE|EG|ER|ES|ET|EU|FI|FJ|FK|FM|FO|FR|GA|GB|GD|GE|GF|GG|GH|GI|GL|GM|GN|GOV|GP|GQ|GR|GS|GT|GU|GW|GY|HK|HM|HN|HR|HT|HU|ID|IE|IL|IM|IN|INFO|INT|IO|IQ|IR|IS|IT|JE|JM|JO|JOBS|JP|KE|KG|KH|KI|KM|KN|KP|KR|KW|KY|KZ|LA|LB|LC|LI|LK|LR|LS|LT|LU|LV|LY|MA|MC|MD|ME|MG|MH|MIL|MK|ML|MM|MN|MO|MOBI|MP|MQ|MR|MS|MT|MU|MUSEUM|MV|MW|MX|MY|MZ|NA|NAME|NC|NET|NF|NG|NI|NL|NO|NP|NR|NU|NZ|OM|ORG|PA|PE|PF|PG|PH|PK|PL|PM|PN|PR|PRO|PS|PT|PW|PY|QA|RE|RO|RS|RU|RW|SA|SB|SC|SD|SE|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SR|ST|SU|SV|SY|SZ|TC|TD|TEL|TF|TG|TH|TJ|TK|TL|TM|TN|TO|TP|TR|TRAVEL|TT|TV|TW|TZ|UA|UG|UK|US|UY|UZ|VA|VC|VE|VG|VI|VN|VU|WF|WS|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|YE|YT|YU|ZA|ZM|ZW))'

    if re.match(ip_regex, indicator):
        return "IPv4"
    # TODO: Update domain name validation (cf. #15)
    elif re.match(domain_regex, indicator, re.IGNORECASE):
        return "FQDN"
    else:
        return None
    
def read_plain_text(response,mapping):
    """ reads a plaintext file with a one indicator per line format """
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
            i = line.split()[0]
            data.append({mapping[0]:i})
    return data
    
def headless_xsv(response, mapping, delimiter=',',quotechar='"'):
    """ reads a headless xsv"""
    raw_data=[]
    for row in csv.reader(StringIO.StringIO(response),delimiter=delimiter,quotechar=quotechar):
        row_data={}
#        print row
        if len(mapping)==len(row):
            for indx,val in enumerate(row):
                row_data[mapping[indx]]=val
            raw_data.append(row_data)
        else:
            print "can't parse: "+str(row)
    return raw_data

def headed_xsv(response, mapping, delimiter=","):
    """ reads an xsv file with the given delimiter and reading the headers fromt the file"""
    raw_data = []
    for row in csv.DictReader(response,delimiter=delimiter):
        raw_row={}
        for col in row.keys():
            if col in mapping.keys():
                raw_row[mapping[col]]=row[col]
            else:
                raw_row[col]=row[col]
        raw_data.append(raw_row)
    return raw_data