import pytest
from app.tasks import add, count_words, divide
from dramatiq.results.errors import ResultError


def test_count_words(stub_broker, stub_worker):
    # Given
    text = "Hello, world!"

    # When
    result = count_words.send(text)
    stub_broker.join(count_words.queue_name)
    stub_worker.join()

    # Then
    assert stub_broker.queues["default"].qsize() == 0
    assert result.get_result() == 2


def test_add_two_positive_integers(stub_broker, stub_worker):
    # Given
    NUM_1 = 1
    NUM_2 = 2
    EXPECTED = 3

    # When
    result = add.send(NUM_1, NUM_2)
    stub_broker.join(add.queue_name)
    stub_worker.join()

    # Then
    assert stub_broker.queues["default"].qsize() == 0
    assert result.get_result() == EXPECTED


def test_divide_on_zero_returns_nothing_but_result_error(stub_broker, stub_worker):
    # Given
    NUM_1 = 1
    NUM_2 = 0

    # When
    result = divide.send(NUM_1, NUM_2)
    stub_broker.join(divide.queue_name)
    stub_worker.join()

    # Then
    assert stub_broker.queues["default"].qsize() == 0
    with pytest.raises(ResultError):
        result.get_result()
