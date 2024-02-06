import csv
import speedtest
import sys

from datetime import datetime, timedelta
from time import sleep


def file_exsists(out_csv):
    try:
        with open(out_csv, 'r+'):
            return (True)
    except (FileNotFoundError):
        return (False)


def create_file(out_csv):
    csv_flle = open(out_csv, 'a')
    csv_flle.close()


def headers_exsist(out_csv):
    with open(out_csv, 'r') as csvfile:
        reader = csv.reader(csvfile)
        try:
            row = ','.join(next(reader))
        except (StopIteration):
            return (False)
        else:
            sniffer = csv.Sniffer()
            return (sniffer.has_header(row))


def write_headers(out_csv, headers):
    with open(out_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(headers)
def headers_match(out_csv, headers):
    with open(out_csv,'r') as csvfile: 
        reader = csv.reader(csvfile, delimiter = ',')
        file_headers = next(reader)
        return(file_headers)
        return (file_headers == headers)


def periodic_speedtest(outfile, results_to_report):
    current_test = setup_speedtest()
    run_speedtest(current_test)
    results = filter_results(current_test, results_to_report)
    results['download'] *= BitsToMegaBits
    results['upload'] *= BitsToMegaBits
    results['isp'] = get_from_client(current_test, 'isp')
    write_results(results, outfile, results_to_report)


def setup_speedtest():
    s = speedtest.Speedtest()
    return (s)


def run_speedtest(test):
    test.get_best_server()
    test.download()
    test.upload()


def get_from_client(test, key):
    return (test.results.dict()['client'][key])


def filter_results(test, keys):
    results_dict = test.results.dict()
    results_dict = {k: v for k, v in results_dict.items() if k in keys}
    return (results_dict)


def write_results(results, out_csv, results_to_report):
    with open(out_csv, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results_to_report)
        writer.writerow(results)


def progress_msg(number_of_tests, test_number):
    if number_of_tests > 0:
        return (f'Running test {test_num} of {number_of_tests}')
    else:
        return (f'Running test number {test_num}')


results_to_report = ['timestamp', 'download', 'upload', 'ping', 'isp']
headers = ['Timestamp',
           'Upload(Mb/s)',
           'Download(Mb/s)',
           'Ping',
           'ISP']

outfile = "speedtest_results.csv"
hours_between_tests = 0.5
number_of_tests = 0   # 0 or less will run until the process is ended
BitsToMegaBits = 1e-6
hours_to_seconds = 3600

headers_do_not_match_str = (f"Warning: The headers in {outfile} "
                            "do not match the variable 'headers'."
                            "Continue? [y/n]")

if not file_exsists(outfile):
    print(f'Creating {outfile}')
    create_file(outfile)
if not headers_exsist(outfile):
    write_headers(outfile, headers)
if not headers_match(outfile, headers):
    print(f'{headers_match(outfile, headers)}')
    print(f'{headers}')
    if not input(headers_do_not_match_str).lower() == 'y':
        sys.exit()

test_num = 1

while True:
    print(progress_msg(number_of_tests, test_num))
    periodic_speedtest(outfile, results_to_report)
    print(f'wrote to {outfile}')
    next_test_time = (datetime.now() +
                      timedelta(hours=hours_between_tests))
    next_test_time = next_test_time.strftime('%H:%M:%S')
    if number_of_tests > 0 and test_num == number_of_tests:
        break
    test_num += 1
    print(f'Next test at {next_test_time}')
    sleep(hours_between_tests * hours_to_seconds)
