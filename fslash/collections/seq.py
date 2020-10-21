"""Sequence module.

Contains a collection of static methods (functions) for operating on
sequences. A sequence is a thin wrapper around `Iterable` so all
functions take (and return) Python iterables.

All functions takes the source as the last curried
argument, i.e all functions returns a function that takes the source
sequence as the only argument.

Example:
    >>> xs = Seq([1, 2, 3])
    >>> ys = xs.pipe(
        Seq.map(lambda x: x + 1),
        Seq.filter(lambda x: x < 3)
    )
"""

import builtins
import functools
import itertools
import sys
from typing import Any, Callable, Iterable, Iterator, Tuple, TypeVar, overload

from fslash.core import pipe

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


class Seq(Iterable[TSource]):
    """Sequence type.

    Contains instance methods for dot-chaining operators methods on
    sequences.

    Example:
        >>> xs = Seq([1, 2, 3])
        >>> ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)
    """

    def __init__(self, iterable: Iterable[TSource] = []) -> None:
        self._value = iterable

    def filter(self, predicate: Callable[[TSource], bool]) -> "Seq[TSource]":
        return Seq(filter(predicate)(self))

    def collect(self, mapping: Callable[[TSource], "Seq[TResult]"]) -> "Seq[TResult]":
        return Seq(collect(mapping)(self))

    def fold(self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
        """Applies a function to each element of the collection,
        threading an accumulator argument through the computation. If
        the input function is f and the elements are i0...iN then
        computes f (... (f s i0)...) iN

        Args:
            folder: A function that updates the state with each element
                from the sequence.
            state: The initial state.
        Returns:
            The state object after the folding function is applied to
            each element of the sequence.
        """
        return functools.reduce(folder, self, state)  # type: ignore

    def head(self) -> TSource:
        """Returns the first element of the sequence."""

        return head(self)

    def map(self, mapper: Callable[[TSource], TResult]) -> "Seq[TResult]":
        """Map sequence.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            The result sequence.
        """

        return Seq(map(mapper)(self))

    def match(self, *args: Any, **kw: Any) -> Any:
        from pampy import match  # type: ignore

        return match(self, *args, **kw)  # type: ignore

    @overload
    def pipe(self, __fn1: Callable[["Seq[TSource]"], TResult]) -> TResult:
        ...

    @overload
    def pipe(self, __fn1: Callable[["Seq[TSource]"], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(self, __fn1: Callable[["Seq[TSource]"], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Seq[TSource]"], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe sequence through the given functions."""
        return pipe(self, *args)

    def scan(self, scanner: Callable[[TState, TSource], TState], state: TState) -> Iterable[TState]:
        """Like fold, but computes on-demand and returns the sequence of
        intermediary and final results.

        Args:
            scanner: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The resulting sequence of computed states.
        """
        return Seq(itertools.accumulate(self, scanner, initial=state))  # type: ignore

    def zip(self, other: Iterable[TResult]) -> Iterable[Tuple[TSource, TResult]]:
        """Combines the two sequences into a list of pairs. The two
        sequences need not have equal lengths: when one sequence is
        exhausted any remaining elements in the other sequence are
        ignored.

        Args:
            other: The second input sequence.

        Returns:
            The result sequence.
        """
        return builtins.zip(self, other)

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for sequence."""
        return builtins.iter(self._value)


def collect(mapping: Callable[[TSource], Iterable[TResult]]) -> Callable[[Iterable[TSource]], Iterable[TResult]]:
    def _collect(source: Iterable[TSource]) -> Iterable[TResult]:
        return (x for xs in source for x in mapping(xs))

    return _collect


def concat(*iterables: Iterable[TSource]) -> Iterable[TSource]:
    """Combines the given variable number of enumerations and/or
    enumeration-of-enumerations as a single concatenated
    enumeration.

    Args:
        iterables: The input enumeration-of-enumerations.

    Returns:
        The result sequence.
    """

    for it in iterables:
        for element in it:
            yield element


empty: Seq[Any] = Seq()
"""The empty sequence."""


def filter(predicate: Callable[[TSource], bool]) -> Callable[[Iterable[TSource]], Iterable[TSource]]:
    """Filter sequence.

    Filters the sequence to a new sequence containing only the
    elements of the sequence for which the given predicate returns
    `True`.

    Args:
        predicate: A function to test whether each item in the
            input sequence should be included in the output.
        source: (curried) The input sequence to to filter.

    Returns:
        A partially applied filter function.
    """

    def _filter(source: Iterable[TSource]) -> Iterable[TSource]:
        """Filter sequence (partially applied).

        Args:
            source: The input sequence to to filter.

        Returns:
            Returns a new collection containing only the elements
            of the collection for which the given predicate returns
            `True`.
        """
        return builtins.filter(predicate, source)

    return _filter


def fold(folder: Callable[[TState, TSource], TState], state: TState) -> Callable[[Iterable[TSource]], TState]:
    """Applies a function to each element of the collection,
    threading an accumulator argument through the computation. If
    the input function is f and the elements are i0...iN then
    computes f (... (f s i0)...) iN

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        Partially applied fold function that takes a source sequence and
        returns the state object after the folding function is applied
        to each element of the sequence.
    """

    def _fold(source: Iterable[TSource]) -> TState:
        """Partially applied fold function.
        Returns:
            The state object after the folding function is applied
            to each element of the sequence.
        """
        return functools.reduce(folder, source, state)  # type: ignore

    return _fold


def fold_back(folder: Callable[[TSource, TState], TState], source: Iterable[TSource]) -> Callable[[TState], TState]:
    """Applies a function to each element of the collection,
    starting from the end, threading an accumulator argument through
    the computation. If the input function is f and the elements are
    i0...iN then computes f i0 (... (f iN s)...)

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        Partially applied fold_back function.
    """

    def _fold_back(state: TState) -> TState:
        """Partially applied fold_back function.

        Returns:
            The state object after the folding function is applied
            to each element of the sequence.
        """
        return functools.reduce(lambda x, y: folder(y, x), reversed(source), state)  # type: ignore

    return _fold_back


def head(source: Iterable[TSource]) -> TSource:
    """Return the first element of the sequence.

    Args:
        source: The input sequence.

    Returns:
        The first element of the sequence.

    Raises:
        Raises `ValueError` if the source sequence is empty.
    """

    for value in source:
        return value
    else:
        raise ValueError("Sequence contains no elements")


def init_infinite(initializer: Callable[[int], TSource]) -> Iterable[TSource]:
    """Generates a new sequence which, when iterated, will return
    successive elements by calling the given function. The results of
    calling the function will not be saved, that is the function will be
    reapplied as necessary to regenerate the elements. The function is
    passed the index of the item being generated.

    Iteration can continue up to `sys.maxint`.
    """
    for i in range(sys.maxsize):
        yield initializer(i)


def iter(action: Callable[[TSource], None]) -> Callable[[Iterable[TSource]], None]:
    """Applies the given function to each element of the collection.

    Args:
        action: A function to apply to each element of the sequence.

    Returns:
        A partially applied iter function.
    """

    def _iter(source: Iterable[TSource]) -> None:
        """A partially applied iter function.

        Note that this function is a pure side effect and returns nothing.

        Args:
            source: The input sequence to apply action to.

        Returns:
            None
        """
        for x in source:
            action(x)

    return _iter


def map(mapper: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], Iterable[TResult]]:
    """Map source sequence.

    Builds a new collection whose elements are the results of
    applying the given function to each of the elements of the
    collection.

    Args:
        mapping: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def _map(source: Iterable[TSource]) -> Iterable[TResult]:
        """Partially applied map function.

        Args:
            source: The input sequence.
        Returns:
            The result sequence.
        """
        return (mapper(x) for x in source)

    return _map


def max(source: Iterable[TSource]) -> TSource:
    """Returns the greatest of all elements of the sequence,
    compared via `max()`."""

    return builtins.max(source)


def max_by(projection: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], TResult]:
    def _max_by(source: Iterable[TSource]) -> TResult:
        return builtins.max(projection(x) for x in source)

    return _max_by


def min(source: Iterable[TSource]) -> TSource:
    """Returns the smallest of all elements of the sequence,
    compared via `max()`."""

    return builtins.min(source)


def min_by(projection: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], TResult]:
    def _min_by(source: Iterable[TSource]) -> TResult:
        return builtins.min(projection(x) for x in source)

    return _min_by


def of(value: Iterable[TSource]) -> Seq[TSource]:
    return Seq(value)


of_list = of
"""Alias to `Seq.of`."""

of_iterable = of
"""Alias to `Seq.of`."""


def scan(
    scanner: Callable[[TState, TSource], TState], state: TState
) -> Callable[[Iterable[TSource]], Iterable[TState]]:
    """Like fold, but computes on-demand and returns the sequence of
    intermediary and final results.

    Args:
        scanner: A function that updates the state with each element
            from the sequence.
        state: The initial state.
    """

    def _scan(source: Iterable[TSource]) -> Iterable[TState]:
        """Partially applied scan function.
        Args:
            source: The input sequence.
        Returns:
            The resulting sequence of computed states.
        """
        return itertools.accumulate(source, scanner, initial=state)  # type: ignore

    return _scan


def singleton(item: TSource) -> Seq[TSource]:
    """Returns a sequence that yields one item only.

    Args:
        item: The input item.

    Returns:
        The result sequence of one item.
    """
    return Seq([item])


def zip(source1: Iterable[TSource]) -> Callable[[Iterable[TResult]], Iterable[Tuple[TSource, TResult]]]:
    """Combines the two sequences into a list of pairs. The two
    sequences need not have equal lengths: when one sequence is
    exhausted any remaining elements in the other sequence are
    ignored.

    Args:
        source1: The first input sequence.

    Returns:
        Partially applied zip function.
    """

    def _zip(source2: Iterable[TResult]) -> Iterable[Tuple[TSource, TResult]]:
        """Combines the two sequences into a list of pairs. The two
        sequences need not have equal lengths: when one sequence is
        exhausted any remaining elements in the other sequence are
        ignored.

        Args:
            source2: The second input sequence.

        Returns:
            The result sequence.
        """
        return builtins.zip(source1, source2)

    return _zip


__all__ = [
    "Seq",
    "concat",
    "collect",
    "empty",
    "filter",
    "fold",
    "fold_back",
    "head",
    "iter",
    "map",
    "max",
    "min",
    "min_by",
    "of",
    "of_list",
    "of_iterable",
    "scan",
    "singleton",
]
