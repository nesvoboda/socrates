
![Logo](https://i.imgur.com/JyKRlbd.png)

# socrates
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Run tests](https://github.com/nesvoboda/socrates/workflows/Run%20tests/badge.svg)
[![codecov](https://codecov.io/gh/nesvoboda/socrates/branch/master/graph/badge.svg?token=NB9C6688R1)](https://codecov.io/gh/nesvoboda/socrates)

A small testing framework for 42's philosophers.

**New**: now includes Delay-o-meter, a tool to measure sleep inaccuracy

#### Acknowledgements
Big thanks to:

[solaldunckel](https://github.com/solaldunckel) for helping to test this project!

[cacharle](https://github.com/cacharle) for their awesome pull requests that are pushing this project forward!


### What are the tests?

Socrates tests two things.

In _**PERFORMANCE**_ tests, it times how long your program runs in a test case where
no philosophers should die (like 550 210 210). By default, your program should hold on for 40 seconds.

In a _**DEATH TIMING**_ test, we make a philosopher die (sorry!) (example: 100 500 500, a philosopher will die at 100ms).
The output of your program is then parsed to measure how soon your program reported that.

If your delay is more than 10ms, the test is failed!

![A screenshot showing a typical test output](https://i.imgur.com/oJ43M1f.png)

### Delay-o-meter

Different machines perform sleeps with different accuracy. Socrates reports the average delay the machine will add to a 200-millisecond sleep. This can help make sure other stuff running on the computer doesn't interfere with Philosopher timings.

You can also use a standalone tool and check different machines:
```
python3 delay_o_meter.py
```

#### How to interpret the result?

The common-sense standard of a good Philosophers is less than 10ms of delay per one eat-sleep-think cycle (example: 310 150 150 should run forever).

**My personal opinion** is that, therefore, a machine must lose less than **3ms on average** for tests to be accurate. Let me know what you think about that!

### CPU load detector

Another way of making sure nothing prevents your philosophers from working properly, Socrates checks the load of your CPU. If it's overloaded, it will show a message.

Here's an [article](https://www.notion.so/philosophers-VM-c60be9c836084edfbcd9c07e29b429c4) that explains why this is important, especially on a VM.

![A screenshot showing the test output with a message: CPU OVERLOADED! RESULTS MAY BE WRONG](https://i.imgur.com/Nj7Jiey.png)

## Installation

Requirements: python 3.6+, [psutil](https://github.com/giampaolo/psutil/blob/master/INSTALL.rst)

1. Clone the repo
```
git clone https://github.com/nesvoboda/socrates
cd socrates
```

2. Install the prerequisites

```
pip3 install -r requirements.txt
```

If you're in a 42 campus, run this instead:

```
python3 -m pip install -r requirements.txt --user
```

If installation fails on Linux, try this:

```
sudo apt-get install python3.7-dev
```
Thanks to [Mazoise](https://github.com/Mazoise) for this suggestion!


## Configuration

You can edit the variables `N_LONG_TESTS` and `LONG_TEST_LENGTH` to determine how long the preformance tests will last.
My standard is 3 consecutive runs of at least 40 seconds.

## Running the tests

```
python3 socrates.py <path to project folder>
```
