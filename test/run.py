import subprocess
from socrates import socrates



def test_performance_negative():
    #res = subprocess.run("python3 socrates.py test/performance/negative/", shell=True)
    res = socrates('test/performance/negative', True)
    assert res != 0

def test_performance_positive():
    #res = subprocess.run("TEST_MODE=on python3 socrates.py test/performance/positive/", shell=True)
    res = socrates('test/performance/negative', True)
    assert res == 0

def test_death_timing_negative():
    #res = subprocess.run("python3 socrates.py test/death_timing/negative/", shell=True)
    assert res != 0

def test_performance_positive():
    #res = subprocess.run("TEST_MODE=on python3 socrates.py test/death_timing/positive/", shell=True)
    assert res == 0