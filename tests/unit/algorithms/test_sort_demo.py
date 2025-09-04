import pytest
from algolib.algorithms.sort_demo import bubble_sort
from algolib.algorithms.sort_demo import insertion_sort


@pytest.mark.parametrize(
    "data",
    [
        [],
        [1],
        [2, 1],
        [3, 2, 1],
        [5, 1, 4, 2, 8],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [1, 1, 1, 1],
    ],
)
def test_bubble_sort_matches_builtin_sorted(data):
    assert bubble_sort(data) == sorted(data)


def test_bubble_sort_does_not_mutate_input():
    data = [3, 1, 2]
    copy = list(data)
    _ = bubble_sort(data)
    assert data == copy


@pytest.mark.parametrize(
    "data",
    [
        [],
        [1],
        [2, 1],
        [3, 2, 1],
        [5, 1, 4, 2, 8],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [1, 1, 1, 1],
    ],
)
def test_insertion_sort_matches_builtin_sorted(data):
    assert insertion_sort(data) == sorted(data)


def test_insertion_sort_does_not_mutate_input():
    data = [3, 1, 2]
    copy = list(data)
    _ = insertion_sort(data)
    assert data == copy
