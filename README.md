
![Logo](https://i.imgur.com/JyKRlbd.png)

# socrates
A small testing framework for 42's philosophers.

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

![Example](https://i.imgur.com/oJ43M1f.png)

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

## Configuration

You can edit the variables `N_LONG_TESTS` and `LONG_TEST_LENGTH` to determine how long the preformance tests will last.
My standard is 3 consecutive runs of at least 40 seconds.

## Running the tests

```
python3 socrates.py <path to project folder>
```
