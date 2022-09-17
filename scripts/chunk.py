
# Copyright 2022 Mark McLoughlin
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE.txt file.

# Takes a sailwave-produced HTML file containing results for multiple
# classes an splits it into multiple files with subsets of those classes

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

# For each desired output file, we list the classes we want to include
#
# {
#     "2022_AL_class1.htm": [
#         "class_1_irc",
#         "class_1_hph"
#     ],
#     "2022_AL_class2.htm": [
#         "class_2_irc",
#         "class_2_hph"
#     ]
# }

import sys
import json

if len(sys.argv) != 2:
    sys.exit('usage: ' + sys.argv[0] + ' output_files.json < input_file.htm')

output_files = None
with open(sys.argv[1]) as f:
    output_files = json.load(f)

import sys
from enum import Enum

class State(Enum):
    HEADER = 1
    SUMMARY = 2
    RACE = 3
    FOOTER = 4
    NONE = 5

state = State.HEADER
fleet = None
template_header = []
template_footer = []
summaries = {}
races = {}

for line in sys.stdin.readlines():
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
        template_header.append(line)
    elif state == State.FOOTER:
        template_footer.append(line)
    elif state == State.SUMMARY:
        if not fleet in summaries:
            summaries[fleet] = []
        summaries[fleet].append(line)
    elif state == State.RACE:
        if not fleet in races:
            races[fleet] = []
        races[fleet].append(line)

    if state in [State.SUMMARY, State.RACE]:
        if line.startswith(table_end):
            state = State.NONE

for output_file in output_files.keys():
    with open(output_file, "w") as f:
        print("Writing", output_file)
        f.writelines(template_header)
        for fleet in output_files[output_file]:
            f.writelines(summaries[fleet])
        for fleet in output_files[output_file]:
            f.writelines(races[fleet])
        f.writelines(template_footer)
