import sys
import os
import subprocess
from time import sleep
from statistics import mean
import threading
from pathlib import Path

import psutil

# How many 'long' tests are needed
N_LONG_TESTS = 3
# How many seconds must a program run uninterrupted
LONG_TEST_LENGTH = 40


CPU_COUNT = psutil.cpu_count()

# array = []

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# We consider that a CPU is overloaded if its system-wide usage
# is > 50% or 5-minute load average divided by CPU core count
# is more than 1.
def cpu_overloaded():
    if psutil.cpu_percent() > 50:
        return True
    if psutil.getloadavg()[1] / CPU_COUNT > 1:
        return True


def terminate_three(binary):
    if 'philo_three' in binary:
        subprocess.run(['killall', 'philo_three'])


def assert_runs_for_at_least(command, seconds, binary, test_name):
    # Run a given command
    f = open(
        f"./test_output/{binary[binary.rfind('/'):]}_{test_name}_out.txt",
        "w")
    cpu_warning_issued = 0
    process = subprocess.Popen(command, stdout=f,
                               shell=True)
    # Wait for some time
    code = process.poll()
    slept = 0
    while (slept < seconds):
        sleep(1)
        slept += 1
        if not cpu_warning_issued and cpu_overloaded():
            print(f"{bcolors.FAIL}\nCPU OVERLOADED! "
                  f"RESULTS MAY BE WRONG!\n{bcolors.ENDC}")
            cpu_warning_issued = True
        code = process.poll()
        # Exit immediately, if the process has died
        if code is not None:
            f.close()
            terminate_three(binary)
            return False

    code = process.poll()
    if code is None:
        # If the process is still running, the test has passed
        process.kill()
        f.close()
        print(f"{bcolors.OKGREEN}[{seconds} SEC] {bcolors.ENDC}", end="", flush=True)
        terminate_three(binary)
        return True
    # If the process isn't running anymore, the test has failed
    f.close()
    terminate_three(binary)
    return False


def measure_starvation_timing(binary, array):
    # Run a philosopher binary with deadly parameters
    data = subprocess.getoutput(f"{binary} 3 310 200 100")
    
    # Get the time of death
    last_line = data[data.rfind('\n') + 1:]
    death_time = int(last_line[:last_line.find(' ')])
    result = death_time - 310
    # Append the delay to the array of results
    array.append(result)
    terminate_three(binary)


def run_long_test(binary, test, test_name):
    for i in range(0, N_LONG_TESTS):
        res = assert_runs_for_at_least(
            f"{binary} {test}",
            LONG_TEST_LENGTH,
            binary,
            f"{test_name}_{i}")
        if res is False:
            print(f"\n\n ❌ {binary} failed test {test}")
            return False
    print(f"\n\n✅  Pass!\n")
    return True


def run_starvation_measures(binary):
    results = []
    for i in range(10):
        measure_starvation_timing(binary, results)
        if results[-1] > 10:
            print(f"\n\n ❌ {binary} failed death timing test :(")
            return False
        else:
            print(f"{bcolors.OKGREEN}[{results[-1]} MS] "
                  f"{bcolors.ENDC}", end="")
    print(f"\n\n✅  Average delay: {mean(results)} ms!\n\n")
    return True


def test_program(binary):
    print(f"\n{bcolors.BOLD}PERFORMANCE{bcolors.ENDC}\n")
    is_three = 'philo_three' in binary
    if is_three:
        print(f"{bcolors.WARNING}WARNING: for philo_three, we will have to run\n"
                "'killall philo_three' after each run. It may stop other running\n"
                f"instances of this program.{bcolors.ENDC}")
    print(f"{bcolors.WARNING}4 410 200 200{bcolors.ENDC}     ", end="", flush=True)
    if run_long_test(binary, "4 410 200 200", 'performance_1') is False:
        return False
    print(f"{bcolors.WARNING}5 800 200 200{bcolors.ENDC}     ", end="", flush=True)
    if run_long_test(binary, "5 800 200 200", 'performance_2') is False:
        return False
    print(f"\n{bcolors.BOLD}DEATH TIMING{bcolors.ENDC}\n")
    if run_starvation_measures(binary) is False:
        return False
    return True


def cpu_waning():
    if cpu_overloaded():
        print(f"{bcolors.FAIL}WARNING! The CPU usage is {psutil.cpu_percent()}"
              f", 5-minute load average is {psutil.getloadavg}.\n"
              f"The test results may be wrong! {bcolors.endc}")


def make_all_binaries(bin_path):
    subprocess.run(["make", "-C", f"{bin_path}/philo_one/"])
    subprocess.run(["make", "-C", f"{bin_path}/philo_two/"])
    subprocess.run(["make", "-C", f"{bin_path}/philo_three/"])


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc > 1 and argc < 3:
        bin_path = sys.argv[1]
    elif argc > 3 or argc == 1:
        print(f"Usage: {sys.argv[0]} <path to project folder>")
        exit(1)

    print(f"\n{bcolors.OKBLUE}-- MAKING BINARIES ---{bcolors.ENDC} \n")
    make_all_binaries(bin_path)
    print(f"\n{bcolors.OKBLUE}--- TEST DESCRIPTION ---{bcolors.ENDC}")
    print(f"\n{bcolors.BOLD}PERFORMANCE.{bcolors.ENDC}\n\n"
          "In these tests, philosophers must not die.\n"
          f"We will run each of the tests {N_LONG_TESTS} times.\n"
          "Test will pass, if your program runs for more than\n"
          f"{LONG_TEST_LENGTH} seconds every time.")
    print(f"\n{bcolors.BOLD}DEATH TIMING{bcolors.ENDC}\n\n"
          "In this test, one philosopher must die.\n"
          "We will check the time of their death, and make sure\n"
          "their death is showed within 10ms of their death.\n\n"
          f"{bcolors.WARNING}This test will only work if your binary prints\n"
          f"nothing but numbers in the timestamp, followed\n"
          f"by a whitespace, like this: 00000000045 3 died{bcolors.ENDC}")
    print(f"\n{bcolors.FAIL}{bcolors.BOLD}WARNING: THIS TEST WILL TAKE AT LEAST\n"
           f"{bcolors.ENDC}{bcolors.FAIL}{LONG_TEST_LENGTH * 6 * N_LONG_TESTS}"
           " SECONDS.\n\nFAILING THIS TEST != A BAD PROJECT\n"
           "PASSING THIS TEST != A GOOD ONE\n"
           f"MAKE YOUR OWN DECISIONS{bcolors.ENDC}\n")
    Path("./test_output/").mkdir(parents=True, exist_ok=True)
    print(f"\n{bcolors.OKBLUE}---------- PHILO_ONE ----------{bcolors.ENDC}\n")
    test_program(f'{bin_path}/philo_one/philo_one')
    print(f"\n{bcolors.OKBLUE}---------- PHILO_TWO ----------{bcolors.ENDC}\n")
    test_program(f'{bin_path}/philo_two/philo_two')
    print(f"\n{bcolors.OKBLUE}---------- PHILO_THREE ----------{bcolors.ENDC}\n")
    test_program(f'{bin_path}/philo_three/philo_three')


