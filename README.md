
![Logo](https://i.imgur.com/JyKRlbd.png)

# socrates
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


A small testing framework for 42's philosophers.

_Big thanks to [solaldunckel](https://github.com/solaldunckel) for helping to test this project!_

## Description

Testing philosophers is a tedious task. You have to run the binaries a lot of time.

In some tests, philosopher shouldn't die for a long time.
Also, you should print out philosopher deaths in no more than 10ms.

Socrates checks these two requrements for you!

### What is inside?

It provides two series of tests: PERFORMANCE and DEATH TIMING.

In a PERFORMANCE test, a binary is launched with a long-living test, and then the script times its execution.
In this tests, philosophers must not die by problem condition.
If the binary exits prematurely (sooner than 40s by default) the test is failed.

In a DEATH TIMING test, a binary is launched with a test, in which a philosopher must die instantly. The program output
is then parsed to measure the delay.

If your delay is more than 10ms, the test is failed!

It will print a nice average for you if you pass the test.

![A screenshot showing a typical test output](https://i.imgur.com/oJ43M1f.png)

### CPU load detector

If your CPU is loaded, your philosophers can die for no reason. The CPU will just get stuck on a task and forget to return to your starving philosophers in time.
So Socrates checks your CPU load constantly and will tell you if the test results can be wrong because of insufficient processing resources.

![A screenshot showing the test output with a message: CPU OVERLOADED! RESULTS MAY BE WRONG](https://i.imgur.com/Nj7Jiey.png)

## Installation

Requirements: python 3

1. Clone the repo
```
git clone https://github.com/nesvoboda/socrates
cd socrates
```

2. Install the prerequisites

```
pip3 install psutil
```

If you're in a 42 campus, run this instead:

```
python3 -m pip install psutil -user
```

## Configuration

You can edit the variables `N_LONG_TESTS` and `LONG_TEST_LENGTH` to determine how long the preformance tests will last.
My standard is 3 consecutive runs of at least 40 seconds.

## Running the tests

```
python3 socrates.py <path to project folder>
```
