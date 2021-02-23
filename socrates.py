#!/usr/bin/env python3

import os
import subprocess
import shlex
import argparse
import textwrap
from time import sleep
from statistics import mean
from pathlib import Path
import re
import psutil
from tqdm import tqdm
from delay_o_meter import measure

import sys

if "pytest" in sys.modules or "PHILO_TEST" in os.environ:
    import test_config as config
else:
    import config


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
    if psutil.getloadavg()[1] / config.CPU_COUNT > 1:
        return True


# This function will try to detect if your binary is still running
# (this sometimes happens with philo_three)
def processes_still_running(binary):
    try:
        executable = binary[binary.rfind("/") + 1 :]
    except Exception:
        executable = binary
    procs = psutil.process_iter(["name"])
    for proc in procs:
        if proc.info["name"] == executable:
            proc.terminate()
            proc.wait()


def assert_runs_for_at_least(command, seconds, binary, test_name):
    # Run a given command
    # f = open(f"./test_output/{binary[binary.rfind('/'):]}_{test_name}_out.txt", "w")
    cpu_warning_issued = 0
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL)
    # Wait for some time
    code = process.poll()
    slept = 0
    for _ in tqdm(range(seconds)):
        if not slept < seconds:
            break
        sleep(0.3)
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
            # f.close()
            return False

    code = process.poll()
    if code is None:
        # If the process is still running, the test has passed
        process.kill()
        process.poll()
        # f.close()
        return True
    # If the process isn't running anymore, the test has failed
    # f.close()
    return False


def parse_death_line(line):
    """
    Parse the last line printed by a philosopher binary, returning the
    death time.
    Ex.:
    00000100 3 died
    should return 100.
    """
    pattern = re.compile(config.SEPARATOR_REGEXP)
    separator_index = pattern.search(line).start()
    death_time = int(line[:separator_index].strip("\0"))
    return death_time


def measure_starvation_timing(binary):
    # Run a philosopher binary with deadly parameters
    data = subprocess.getoutput(f"{binary} {config.DEATH_TIMING_TEST}")
    print(data)
    if data[-1] == "\0":
        data = data[:-2]
    pattern = re.compile(config.SEPARATOR_REGEXP)
    # Get the start time
    first_line = data[: data.find("\n")]

    separator_index = pattern.search(first_line).start()
    start_time = int(first_line[:separator_index])

    # Get the time of death
    last_line = data[data.rfind("\n") + 1 :]

    separator_index = pattern.search(last_line).start()
    death_time = parse_death_line(last_line)
    result = abs(death_time - start_time - config.DEATH_TIMING_OPTIMUM)
    # Append the delay to the array of results
    # array.append(result)
    return result


def run_long_test(binary, test, test_name):
    for i in range(0, config.N_LONG_TESTS):
        res = assert_runs_for_at_least(
            f"{binary} {test}", config.LONG_TEST_LENGTH, binary, f"{test_name}_{i}"
        )
        processes_still_running(binary)
        if res is False:
            print(f"\n\n ❌ {binary} failed test {test}")
            config.FAIL = 1
            return False
    print(f"\n\n✅  Pass!\n")
    return True


def run_starvation_measures(binary):
    results = []
    for i in range(config.N_DEATH_TIMING_TESTS):
        results.append(measure_starvation_timing(binary))
        processes_still_running(binary)
        if results[-1] > 10:
            print(f"\n\n ❌ {binary} failed death timing test :(")
            config.FAIL = 1
            return False
        else:
            print(
                f"{bcolors.OKGREEN}[{results[-1]} MS] " f"{bcolors.ENDC}",
                end="",
                flush=True,
            )
    if config.N_DEATH_TIMING_TESTS > 0:
        print(f"\n\n✅  Average delay: {mean(results)} ms!\n\n")
    return True


def test_program(binary):
    print(f"\n{bcolors.BOLD}PERFORMANCE{bcolors.ENDC}\n")
    print(f"{bcolors.WARNING}{config.EVEN_NUMBER_TEST}{bcolors.ENDC}     ", flush=True)
    if run_long_test(binary, config.EVEN_NUMBER_TEST, "performance_1") is False:
        return False
    print(f"{bcolors.WARNING}{config.ODD_NUMBER_TEST}{bcolors.ENDC}     ", flush=True)
    if run_long_test(binary, config.ODD_NUMBER_TEST, "performance_2") is False:
        return False
    print(f"\n{bcolors.BOLD}DEATH TIMING{bcolors.ENDC}\n")
    if run_starvation_measures(binary) is False:
        return False
    return True


def cpu_warning():
    if cpu_overloaded():
        print(
            f"{bcolors.FAIL}WARNING! The CPU usage is {psutil.cpu_percent()}"
            f", 5-minute load average is {psutil.getloadavg}.\n"
            f"The test results may be wrong! {bcolors.ENDC}"
        )


def make_all_binaries(bin_path):
    subprocess.run(["make", "-C", f"{bin_path}/philo_one/"])
    subprocess.run(["make", "-C", f"{bin_path}/philo_two/"])
    subprocess.run(["make", "-C", f"{bin_path}/philo_three/"])


def print_test_description():
    print(
        f"\n{bcolors.BOLD}PERFORMANCE.{bcolors.ENDC}\n\n"
        "In these tests, philosophers must not die.\n"
        f"We will run each of the tests {config.N_LONG_TESTS} times.\n"
        "Test will pass, if your program runs for more than\n"
        f"{config.LONG_TEST_LENGTH} seconds every time."
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
        f"{bcolors.ENDC}{bcolors.FAIL}{config.LONG_TEST_LENGTH * 6 * config.N_LONG_TESTS}"
        " SECONDS.\n\nFAILING THIS TEST != A BAD PROJECT\n"
        "PASSING THIS TEST != A GOOD ONE\n"
        f"MAKE YOUR OWN DECISIONS{bcolors.ENDC}\n"
    )


def measure_system_delay():
    avgs = []

    print("Measuring system delay", end="", flush=True)
    for i in range(0, 20):
        print(".", end="", flush=True)
        avgs.append(measure())
    print("\n")

    print(
        f"For 200ms of usleep this machine adds {mean(avgs):.3f}ms of delay on average"
    )
    print(f"Peak delay: {max(avgs):.3f}ms")
    if mean(avgs) > 2:
        print(
            f"{bcolors.WARNING}Please note that a significant delay may impact the performance of philosophers.{bcolors.ENDC}"
        )
        sleep(5)


def socrates(bin_path, philo_num):

    print(f"\n{bcolors.OKBLUE}-- DELAY-O-METER ---{bcolors.ENDC} \n")
    measure_system_delay()
    cpu_warning()
    print(f"\n{bcolors.OKBLUE}-- MAKING BINARIES ---{bcolors.ENDC} \n")
    make_all_binaries(bin_path)
    print(f"\n{bcolors.OKBLUE}--- TEST DESCRIPTION ---{bcolors.ENDC}")

    print_test_description()
    Path("./test_output/").mkdir(parents=True, exist_ok=True)

    if os.path.isfile(f"{bin_path}/philo_one/philo_one") and (
        philo_num == 0 or philo_num == 1
    ):
        print(f"\n{bcolors.OKBLUE}---------- PHILO_ONE ----------{bcolors.ENDC}\n")
        test_program(f"{bin_path}/philo_one/philo_one")
    if os.path.isfile(f"{bin_path}/philo_two/philo_two") and (
        philo_num == 0 or philo_num == 2
    ):
        print(f"\n{bcolors.OKBLUE}---------- PHILO_TWO ----------{bcolors.ENDC}\n")
        test_program(f"{bin_path}/philo_two/philo_two")
    if os.path.isfile(f"{bin_path}/philo_three/philo_three") and (
        philo_num == 0 or philo_num == 3
    ):
        print(f"\n{bcolors.OKBLUE}---------- PHILO_THREE ----------{bcolors.ENDC}\n")
        test_program(f"{bin_path}/philo_three/philo_three")
    if config.FAIL == 1:
        return 1
    else:
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test for the philosophers project",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--philo",
        help=textwrap.dedent(
            """\
            Number of the philosopher program to test
             - 1: philo_one
             - 2: philo_two
             - 3: philo_three
             - 0: all programs (default)
        """
        ),
        type=int,
        choices=[0, 1, 2, 3],
        default=0,
    )
    parser.add_argument(
        "-n", default=config.N_LONG_TESTS, type=int, help="number of long test"
    )
    parser.add_argument(
        "-t", default=config.LONG_TEST_LENGTH, type=int, help="long test time"
    )
    parser.add_argument("path", help="path to project folder")

    args = parser.parse_args()
    config.N_LONG_TESTS = args.n
    config.LONG_TEST_LENGTH = args.t
    try:
        exit(socrates(args.path, args.philo))
    except KeyboardInterrupt:
        pass
