from socrates import socrates


def test_performance_positive():
    res1 = socrates('test/performance/positive', True, True)
    print(f"res1 is {res1}")
    assert res1 == 0

def test_performance_negative():
    res = socrates('test/performance/negative')
    assert res != 0

def test_death_timing_positive():
    res3 = socrates('test/death_timing/positive', True)
    assert res3 == 0

def test_death_timing_negative():
    res2 = socrates('test/death_timing/negative', True)
    assert res2 != 0
