import psutil

# How many 'long' tests are needed
N_LONG_TESTS = 2

# How many seconds must a program run uninterrupted
LONG_TEST_LENGTH = 2

# The test that will be used for an even number of philosophers
EVEN_NUMBER_TEST = "4 311 150 150"

# The test that will be used for and odd number of philosophers
ODD_NUMBER_TEST = "5 600 150 150"

# The test that will be used for the death timing tests
DEATH_TIMING_TEST = "3 310 200 100"

# The death timing target (a philosopher should ideally die at this moment)
DEATH_TIMING_OPTIMUM = 310

N_DEATH_TIMING_TESTS = 3

# The regexp that matches the character that separates your
# timestamp from your status messages. This is needed to parse your death timing.
# The default is "any whitespace", which will match both
# 000000310\t1 died
# and
# 000000310 1 died
SEPARATOR_REGEXP = r"\s"

CPU_COUNT = psutil.cpu_count()

FAIL = 0
