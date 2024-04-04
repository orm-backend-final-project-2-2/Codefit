import sys
import re

if len(sys.argv) == 2:
    branch_name = sys.argv[1]
    pattern = re.compile(r'.*feature-(\w+)/(.+)')
    matches = pattern.match(branch_name)

    if matches:
        app_name, feature_name = matches.groups()
        words = feature_name.split('-')
        tc_feature_name = ''.join([word.title() for word in words]) + 'TestCase'
        print(f'{app_name} {tc_feature_name}')