from socrates import (
    parse_death_line, measure_starvation_timing, run_starvation_measures)


def test_parse_death_line():
    assert parse_death_line("0000100 3 died") == 100


def test_measure_starvation_timing():
    assert measure_starvation_timing("./tests/death_timing_positive.py") == 5

def test_run_starvation_measures():
    assert run_starvation_measures("./tests/death_timing_positive.py") == True