#
# ~/mocker.py
#
import argparse
import json
import os
import re
import textwrap
import xlsxwriter as xl
import threading

version = "0.1a"
DEFAULT_RESULT_COUNT = 5

sample = """/** create schema in JSON format
eg.
   {
       "api": [
            { "url": "http://target/api", "dataset": "set_name" },
            { "url": "http://target/api2", "dataset": "set_name2" }
       ],
       "randoms": {
            "random_set1": ["value1", "value2", "value3"],
            "random_set2": [1,2,3,4,5,6],
            "random_set3": $set_name.target_field
       },
       "schema": {
            "table_name": {
                "field_name": "static value",
                "field_name1": 1234,
                "field_name2": $set_name.field,
                "field_name3": $set_name2.field,
                "field_name4": $set_name2.field2,
                "rand_field1": $random_set1,
                "rand_field2": $random_set2,
                "rand_field3": $random_set3
            }
       }
   }
*/
"""


def _fetch(url, dataset_name, state):
    if(not url):
        state['errored'] = True
        raise Exception('api url missing')
    if(not dataset_name):
        state['errored'] = True
        raise Exception('api dateset name missing')
    print('sending request to %s' % url)
    print('saving to dataset: %s' % dataset_name)


def configure(config:dict):
    state = {}
    state['db'] = {}
    state['errored'] = False
    apis = config.get('api')
    randoms = config.get('randoms')
    schemas = config.get('schemas')
    print('thread workers: %d' % len(apis))
    print('fetching remote resources...')
    for api in apis:
        threading.Thread(target=_fetch, args=(api['url'], api['dataset'], state)).start()
        # call worker here...


def main(args):
    print("Mocker %s" % version)
    print("Using config file: %s" % args.config)
    print("Target output: %s" % args.out)
    print('--------------')
    if(not os.path.exists(args.config)):
        with open(args.config, 'w') as f:
            f.writelines(sample)
    with open(args.config) as raw:
        text = ''.join(raw)
        refs = re.findall("\$[\w\.]+", text)
        text = re.sub('\$[\w\.]+', '"\g<0>"', text)
        try:
            config = json.loads(text)
            configure(config)
        except json.decoder.JSONDecodeError as e:
            err_meta = re.findall('\d+', e.args[0])
            err_line = int(err_meta[0])
            err_col = int(err_meta[1])
            err_end = int(err_meta[2])
            arr_line = text.splitlines()
            print('----')
            print("%s    <--- ERROR" % text[0 : err_end].strip())
            print('----')
            print('Oops.. %s' % e.args[0])


if __name__ == "__main__":
    cwd = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(prog='Mocker %s' % version, formatter_class=argparse.RawTextHelpFormatter, epilog=textwrap.dedent(sample))
    parser.add_argument("config", type=str, help="mock data configuration .schema file.")
    parser.add_argument("-o", "--out", type=str, default="console", help="console, xlsx, sql")
    parser.add_argument("-c", "--count", type=int, default=DEFAULT_RESULT_COUNT, help="number of results. default = %d" % DEFAULT_RESULT_COUNT)
    args = parser.parse_args();
    main(args)

