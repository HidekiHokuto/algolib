"""
Teaching implementations of basic sorting algorithms.

This module contains simple, dependency-free reference implementations of
classical sorting algorithms. They are intended for educational use and small
inputs, not for performance.
"""

from __future__ import annotations
from typing import List, Sequence


def bubble_sort(arr: Sequence[float]) -> List[float]:
    r"""
    Sort a list using the bubble sort algorithm.

    Parameters
    ----------
    arr : Sequence[float]
        Input sequence of numbers.

    Returns
    -------
    List[float]
        A new list containing the sorted values in ascending order.

    Notes
    -----
    - Time complexity: :math:`\mathcal{O}(n^2)`
    - Space complexity: :math:`\mathcal{O}(1)` extra (besides the output copy)
    - Stable: yes

    This implementation makes a copy of the input and sorts in place.
    """
    a = list(arr)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def insertion_sort(arr: Sequence[float]) -> List[float]:
    r"""
    Sort a list using the insertion sort algorithm.

    Parameters
    ----------
    arr : Sequence[float]
        Input sequence of numbers.

    Returns
    -------
    List[float]
        A new list containing the sorted values in ascending order.

    Notes
    -----
    - Time complexity: :math:`\mathcal{O}(n^2)` in the worst case.
    - Space complexity: :math:`\mathcal{O}(1)` extra (besides the output copy).
    - Stable: yes.

    This implementation makes a copy of the input and sorts in place.
    """
    a = list(arr)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a
