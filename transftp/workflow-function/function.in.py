
FTP_SERVER = "@@FTP_SERVER@@"
FTP_USER = "@@FTP_USER@@"
FTP_PASSWORD = "@@FTP_PASSWORD@@"
FTP_DIR = "@@FTP_DIR@@"

import urllib.parse
import boto3
import io

S3 = boto3.client('s3')

def handler(event, context):
    print("Event: ", event)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    print("Bucket: ", bucket)
    print("Key: ", key)

    if key not in TRANSFORMS:
        print("No tranform config for: ", key)
        return {}

    obj = S3.get_object(Bucket=bucket, Key=key)

    results = parse_results(obj['Body'])

    output_files = transform_results(TRANSFORMS[key], results)

    ftp_upload(output_files)

    response = {}

    print("Response: ", response)

    return response

from ftplib import FTP

# Takes a map of filename to stream
def ftp_upload(files):
    with FTP(FTP_SERVER) as ftp:
        print("Logging into ", FTP_SERVER)
        ftp.login(FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_DIR)

        for name in files.keys():
            print("Uploading ", name)
            ftp.storbinary("STOR " + name, files[name])

class Results:
    def __init__(self):
        self.template_header = []
        self.template_footer = []
        self.summaries = {}
        self.races = {}

import re

# The key lines we look for in the sailwave-produced HTML file are:
#
#  1. The start of a series summary table - <h3 class="summarytitle"

summary_start = '<h3 class="summarytitle"'
summary_re = re.compile('id="summary(.*)"')

#  2. The start of an individual race table - <h3 class="racetitle"

race_start = '<h3 class="racetitle"'
race_re = re.compile('id="r[0-9](.*)"')

#  3. The end of a race or summary table

table_end = '</table>'

#  3. The start of the page footer

footer_start = '<p class="hardleft">'

from enum import Enum

class State(Enum):
    HEADER = 1
    SUMMARY = 2
    RACE = 3
    FOOTER = 4
    NONE = 5

# Takes a sailwave-produced HTML file containing results for multiple
# classes an splits it into a header and footer, and chunks of HTML for
# the series summaries and individual races
def parse_results(s):
    results = Results()

    state = State.HEADER
    fleet = None

    for line in s.iter_lines():
        line = line.decode('utf-8')
        if line.startswith(summary_start):
            state = State.SUMMARY
            m = summary_re.search(line)
            fleet = m.group(1)
        elif line.startswith(race_start):
            state = State.RACE
            m = race_re.search(line)
            fleet = m.group(1)
        elif line.startswith(footer_start):
            state = State.FOOTER

        if state == State.HEADER:
            results.template_header.append(line)
        elif state == State.FOOTER:
            results.template_footer.append(line)
        elif state == State.SUMMARY:
            if not fleet in results.summaries:
                results.summaries[fleet] = []
            results.summaries[fleet].append(line)
        elif state == State.RACE:
            if not fleet in results.races:
                results.races[fleet] = []
            results.races[fleet].append(line)

        if state in [State.SUMMARY, State.RACE]:
            if line.startswith(table_end):
                state = State.NONE

    return results

def transform_results(transforms, results):
    output_files = {}
    for output_file in transforms.keys():
        f = io.BytesIO()
        def writelines(lines):
            l = []
            for s in lines:
                l.append(s.encode('utf-8'))
            f.writelines(l)
        writelines(results.template_header)
        for fleet in transforms[output_file]:
            writelines(results.summaries[fleet])
        for fleet in transforms[output_file]:
            writelines(results.races[fleet])
        writelines(results.template_footer)
        f.seek(0)
        output_files[output_file] = f
    return output_files
