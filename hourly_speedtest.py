import csv
import speedtest
from datetime import datetime, timedelta
from time import sleep

BitsToMegaBits = 1e-6
results_to_report = ['timestamp','download', 'upload', 'ping', 'isp']
outfile = "speedtest_results.csv"
hours_between_tests = 1


hours_to_seconds = 3600

def setup_speedtest():
    s = speedtest.Speedtest()
    s.get_best_server()
    return(s)

def run_speedtest(test):
    test.download()
    test.upload()

def get_from_client(test, key):
    return(test.results.dict()['client'][key])
    
def filter_results(test, keys):
    results_dict = test.results.dict()
    results_dict = {k:v for k,v in results_dict.items() if k in keys}
    return(results_dict)

def write_results(results, out_csv, results_to_report):
    with open(out_csv, 'a', newline='') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames=results_to_report)
        writer.writerow(results)

test_num = 1

while True:
    print(f'Test number {test_num}')
    current_test = setup_speedtest()
    run_speedtest(current_test)
    get_from_client(current_test, 'isp')
    get_from_client(current_test, 'ip')
    results = filter_results(current_test, results_to_report)
    results['download'] *= BitsToMegaBits
    results['upload'] *= BitsToMegaBits
    results['isp'] = get_from_client(current_test, 'isp')
    write_results(results, outfile, results_to_report)
    print(f'Wrote to {outfile}')
    next_test = (datetime.now() + timedelta(hours=hours_between_tests)).strftime('%H:%M:%S')
    print(f'Next test at {next_test}')
    test_num += 1
    sleep(hours_between_tests * hours_to_seconds)

