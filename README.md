
![Logo](https://i.imgur.com/JyKRlbd.png)

# socrates
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


A small testing framework for 42's philosophers.

_Big thanks to [solaldunckel](https://github.com/solaldunckel) for helping to test this project!_

## Description

Testing philosophers is a tedious task. You have to run the binaries over and over, countless times!

![A funny gif](https://media.giphy.com/media/PvvSfSDFoAL5e/giphy.gif)

In general, there are two goals in testing philosophers:
* Program runs for a long time, philosophers don't die when they should live,
* If philosophers die, their death should be shown in less than 10ms.

Socrates checks these two requirements for you!

### What is inside?

It provides two series of tests: PERFORMANCE and DEATH TIMING.

A PERFORMANCE test is a stable test. By its conditions, no philosophers should die.
So this script times the execution of your binary.

If it exits prematurely (sooner than 40s by default) the test is failed.

In a DEATH TIMING test, a philosopher must die instantly. The program output
is then parsed to measure how soon your program reported that.

If your delay is more than 10ms, the test is failed!

It will print a nice average for you if you pass the test.

![A screenshot showing a typical test output](https://i.imgur.com/oJ43M1f.png)

### CPU load detector

If your CPU is loaded, your philosophers can die for no reason. The CPU will just get stuck on a task and forget to return to your starving philosophers in time.
So Socrates checks your CPU load constantly and will tell you if the test results can be wrong because of insufficient processing resources.

Here's an [article](https://www.notion.so/philosophers-VM-c60be9c836084edfbcd9c07e29b429c4) that explains why this is important, especially on a VM.

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
