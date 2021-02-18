from socrates import (
    parse_death_line,
    measure_starvation_timing,
    run_starvation_measures,
    run_long_test,
    os,
    subprocess,
)


def test_parse_death_line():
    assert parse_death_line("0000100 3 died") == 100


def test_measure_starvation_timing_pos():
    assert measure_starvation_timing("./tests/death_timing_positive.py") == 5


def test_measure_starvation_timing_neg():
    assert measure_starvation_timing("./tests/death_timing_negative.py") == 15


def test_run_starvation_measures_pos():
    assert run_starvation_measures("./tests/death_timing_positive.py") is True


def test_run_starvation_measures_neg():
    assert run_starvation_measures("./tests/death_timing_negative.py") is False


def test_long_test_pos():
    assert run_long_test("./tests/long_test_positive.py", "a", "b") is True


def test_long_test_neg():
    assert run_long_test("./tests/long_test_negative.py", "a", "b") is False


def test_integration_positive():
    env = os.environ
    env["PHILO_TEST"] = "True"
    res = subprocess.call(
        "./socrates.py ./tests/integration/positive/", shell=True, env=env
    )
    assert res == 0


def test_integration_fails_long():
    env = os.environ
    env["PHILO_TEST"] = "True"
    res = subprocess.call(
        "./socrates.py ./tests/integration/fails-long/", shell=True, env=env
    )
    assert res == 1


def test_integration_fails_death_timing():
    env = os.environ
    env["PHILO_TEST"] = "True"
    res = subprocess.call(
        "./socrates.py ./tests/integration/fails-timing/", shell=True, env=env
    )
    assert res == 1
