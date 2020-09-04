import sys
import os
import subprocess
from time import sleep
from statistics import mean
import threading
from pathlib import Path
import re
import psutil
import signal

# How many 'long' tests are needed
N_LONG_TESTS = 3

# How many seconds must a program run uninterrupted
LONG_TEST_LENGTH = 40

# The test that will be used for an even number of philosophers
EVEN_NUMBER_TEST = "4 311 150 150"

# The test that will be used for and odd number of philosophers
ODD_NUMBER_TEST = "5 600 150 150"

# The test that will be used for the death timing tests
DEATH_TIMING_TEST = "3 310 200 100"

N_DEATH_TIMING_TESTS = 10

# The regexp that matches the character that separates your
# timestamp from your status messages. This is needed to parse your death timing.
# The default is "any whitespace", which will match both
# 000000310\t1 died
# and
# 000000310 1 died
SEPARATOR_REGEXP = r"\s"

CPU_COUNT = psutil.cpu_count()

FAIL = 0


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# We consider that a CPU is overloaded if its system-wide usage
# is > 50% or 5-minute load average divided by CPU core count
# is more than 1.
def cpu_overloaded():
    if psutil.cpu_percent() > 50:
        return True
    if psutil.getloadavg()[1] / CPU_COUNT > 1:
        return True


# This function will try to detect if your binary is still running
# (this sometimes happens with philo_three)
def processes_still_running(binary):
    try:
        executable = binary[binary.rfind("/") + 1 :]
    except Exception:
        executable = binary
    procs = psutil.process_iter(["name", "status", "pid"])
    for proc in procs:
        if proc.info["name"] == executable and proc.info["status"] == "running":
            proc.terminate()
            proc.wait()


def assert_runs_for_at_least(command, seconds, binary, test_name):
    # Run a given command
    f = open(f"./test_output/{binary[binary.rfind('/'):]}_{test_name}_out.txt", "w")
    cpu_warning_issued = 0
    process = subprocess.Popen(command, stdout=f, shell=True)
    # Wait for some time
    code = process.poll()
    slept = 0
    while slept < seconds:
        sleep(1)
        slept += 1
        if not cpu_warning_issued and cpu_overloaded():
            print(
                f"{bcolors.FAIL}\nCPU OVERLOADED! "
                f"RESULTS MAY BE WRONG!\n{bcolors.ENDC}"
            )
            cpu_warning_issued = True
        code = process.poll()
        # Exit immediately, if the process has died
        if code is not None:
            f.close()
            return False

    code = process.poll()
    if code is None:
        # If the process is still running, the test has passed
        process.kill()
        process.poll()
        f.close()
        print(f"{bcolors.OKGREEN}[{seconds} SEC] {bcolors.ENDC}", end="", flush=True)
        return True
    # If the process isn't running anymore, the test has failed
    f.close()
    return False


def measure_starvation_timing(binary, array):
    # Run a philosopher binary with deadly parameters
    data = subprocess.getoutput(f"{binary} {DEATH_TIMING_TEST}")
    pattern = re.compile(SEPARATOR_REGEXP)
    # Get the start time
    first_line = data[: data.find("\n")]
    separator_index = pattern.search(first_line).start()
    start_time = int(first_line[:separator_index])

    # Get the time of death
    last_line = data[data.rfind("\n") + 1 :]

    separator_index = pattern.search(last_line).start()
    death_time = int(last_line[:separator_index])
    result = death_time - start_time - 310
    # Append the delay to the array of results
    array.append(result)


def run_long_test(binary, test, test_name):
    global FAIL
    for i in range(0, N_LONG_TESTS):
        res = assert_runs_for_at_least(
            f"{binary} {test}", LONG_TEST_LENGTH, binary, f"{test_name}_{i}"
        )
        processes_still_running(binary)
        if res is False:
            print(f"\n\n ❌ {binary} failed test {test}")
            FAIL = 1
            return False
    print(f"\n\n✅  Pass!\n")
    return True


def run_starvation_measures(binary):
    global FAIL
    results = []
    for i in range(N_DEATH_TIMING_TESTS):
        measure_starvation_timing(binary, results)
        processes_still_running(binary)
        if results[-1] > 10:
            print(f"\n\n ❌ {binary} failed death timing test :(")
            FAIL = 1
            return False
        else:
            print(
                f"{bcolors.OKGREEN}[{results[-1]} MS] " f"{bcolors.ENDC}",
                end="",
                flush=True,
            )
    if N_DEATH_TIMING_TESTS > 0:
        print(f"\n\n✅  Average delay: {mean(results)} ms!\n\n")
    return True


def test_program(binary):
    print(f"\n{bcolors.BOLD}PERFORMANCE{bcolors.ENDC}\n")
    print(f"{bcolors.WARNING}{EVEN_NUMBER_TEST}{bcolors.ENDC}     ", end="", flush=True)
    if run_long_test(binary, EVEN_NUMBER_TEST, "performance_1") is False:
        return False
    print(f"{bcolors.WARNING}{ODD_NUMBER_TEST}{bcolors.ENDC}     ", end="", flush=True)
    if run_long_test(binary, ODD_NUMBER_TEST, "performance_2") is False:
        return False
    print(f"\n{bcolors.BOLD}DEATH TIMING{bcolors.ENDC}\n")
    if run_starvation_measures(binary) is False:
        return False
    return True


def cpu_waning():
    if cpu_overloaded():
        print(
            f"{bcolors.FAIL}WARNING! The CPU usage is {psutil.cpu_percent()}"
            f", 5-minute load average is {psutil.getloadavg}.\n"
            f"The test results may be wrong! {bcolors.endc}"
        )


def make_all_binaries(bin_path):
    subprocess.run(["make", "-C", f"{bin_path}/philo_one/"])
    subprocess.run(["make", "-C", f"{bin_path}/philo_two/"])
    subprocess.run(["make", "-C", f"{bin_path}/philo_three/"])


def socrates(bin_path, test_mode=None, no_death_timing=None):
    global N_DEATH_TIMING_TESTS
    global LONG_TEST_LENGTH

    if test_mode:
        LONG_TEST_LENGTH = 1
        N_DEATH_TIMING_TESTS = 1
    if no_death_timing:
        N_DEATH_TIMING_TESTS = 0

    print(f"\n{bcolors.OKBLUE}-- MAKING BINARIES ---{bcolors.ENDC} \n")
    make_all_binaries(bin_path)
    print(f"\n{bcolors.OKBLUE}--- TEST DESCRIPTION ---{bcolors.ENDC}")
    print(
        f"\n{bcolors.BOLD}PERFORMANCE.{bcolors.ENDC}\n\n"
        "In these tests, philosophers must not die.\n"
        f"We will run each of the tests {N_LONG_TESTS} times.\n"
        "Test will pass, if your program runs for more than\n"
        f"{LONG_TEST_LENGTH} seconds every time."
    )
    print(
        f"\n{bcolors.BOLD}DEATH TIMING{bcolors.ENDC}\n\n"
        "In this test, one philosopher must die.\n"
        "We will check the time of their death, and make sure\n"
        "their death is showed within 10ms of their death.\n\n"
        f"{bcolors.WARNING}This test will only work if your binary prints\n"
        f"nothing but numbers in the timestamp, followed\n"
        f"by a whitespace, like this: 00000000045 3 died{bcolors.ENDC}"
    )
    print(
        f"\n{bcolors.FAIL}{bcolors.BOLD}WARNING: THIS TEST WILL TAKE AT LEAST\n"
        f"{bcolors.ENDC}{bcolors.FAIL}{LONG_TEST_LENGTH * 6 * N_LONG_TESTS}"
        " SECONDS.\n\nFAILING THIS TEST != A BAD PROJECT\n"
        "PASSING THIS TEST != A GOOD ONE\n"
        f"MAKE YOUR OWN DECISIONS{bcolors.ENDC}\n"
    )
    Path("./test_output/").mkdir(parents=True, exist_ok=True)
    print(f"\n{bcolors.OKBLUE}---------- PHILO_ONE ----------{bcolors.ENDC}\n")
    test_program(f"{bin_path}/philo_one/philo_one")
    print(f"\n{bcolors.OKBLUE}---------- PHILO_TWO ----------{bcolors.ENDC}\n")
    test_program(f"{bin_path}/philo_two/philo_two")
    print(f"\n{bcolors.OKBLUE}---------- PHILO_THREE ----------{bcolors.ENDC}\n")
    test_program(f"{bin_path}/philo_three/philo_three")
    if FAIL == 1:
        return 1
    else:
        return 0


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc > 1 and argc < 3:
        bin_path = sys.argv[1]
    elif argc > 3 or argc == 1:
        print(f"Usage: {sys.argv[0]} <path to project folder>")
        exit(1)
    exit(socrates(bin_path))
