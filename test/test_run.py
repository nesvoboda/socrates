import subprocess
from socrates import socrates

def test_performance_negative():
    # res = subprocess.run("python3 ../socrates.py performance/negative", shell=True)
    res = socrates('test/performance/negative')
    assert res != 0

def test_performance_positive():
    # res = subprocess.run("TEST_MODE=on NO_DEATH_TIMING=true python3 ../socrates.py performance/positive", shell=True)
    res1 = socrates('test/performance/positive', True, True)
    assert res1 == 0

def test_death_timing_negative():
    # res = subprocess.run("python3 ../socrates.py death_timing/negative", shell=True)
    res2 = socrates('test/death_timing/negative', True)
    assert res2 != 0

def test_death_timing_positive():
    # res = subprocess.run("TEST_MODE=on python3 ../socrates.py death_timing/positive", shell=True)
    res3 = socrates('test/death_timing/positive', True)
    assert res3 == 0