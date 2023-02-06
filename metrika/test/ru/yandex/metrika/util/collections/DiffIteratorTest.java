package ru.yandex.metrika.util.collections;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Random;
import java.util.Set;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterators;
import com.google.common.collect.Sets;
import org.junit.Ignore;
import org.junit.Test;

import static java.util.Comparator.comparing;
import static java.util.function.Predicate.not;
import static java.util.stream.Collectors.counting;
import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.toList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static ru.yandex.metrika.util.collections.DiffItem.added;
import static ru.yandex.metrika.util.collections.DiffItem.removed;
import static ru.yandex.metrika.util.collections.F.id;

public class DiffIteratorTest {

    private static final Comparator<Integer> comparator = Comparator.naturalOrder();

    @Test(expected = NoSuchElementException.class)
    public void testEmptyBoth() {
        var iterator = new DiffIterator<>(comparator, Collections.emptyIterator(), Collections.emptyIterator());

        assertFalse(iterator.hasNext());
        iterator.next(); // throws expected exception
    }

    @Test
    public void testEmptyOld() {
        var iterator = new DiffIterator<>(comparator, Collections.emptyIterator(), Iterators.forArray(1, 2, 3, 4));

        var diffItems = ImmutableList.copyOf(iterator);
        assertEquals(
                List.of(added(1), added(2), added(3), added(4)),
                diffItems
        );
    }

    @Test
    public void testEmptyNew() {
        var iterator = new DiffIterator<>(comparator, Iterators.forArray(1, 2, 3, 4), Collections.emptyIterator());

        var diffItems = ImmutableList.copyOf(iterator);
        assertEquals(
                List.of(removed(1), removed(2), removed(3), removed(4)),
                diffItems
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void testNotSortedOld() {
        var iterator = new DiffIterator<>(comparator, Iterators.forArray(2, 1), Collections.emptyIterator());
        ImmutableList.copyOf(iterator); // drain
    }

    @Test(expected = IllegalArgumentException.class)
    public void testNotSortedNew() {
        var iterator = new DiffIterator<>(comparator, Collections.emptyIterator(), Iterators.forArray(2, 1));
        ImmutableList.copyOf(iterator); // drain
    }

    @Test
    public void testBothNonEmpty() {
        var iterator = new DiffIterator<>(comparator, Iterators.forArray(1, 2, 4, 5, 7), Iterators.forArray(3, 4, 5, 6, 8, 9));

        var diffItems = ImmutableList.copyOf(iterator);
        assertEquals(
                List.of(removed(1), removed(2), added(3), added(6), removed(7), added(8), added(9)),
                diffItems
        );
    }

    @Test
    public void testRepeatedElementsWithSkip() {
        var iterator = new DiffIterator<>(comparator, Iterators.forArray(1, 1, 2, 3, 3, 3), Iterators.forArray(2, 2, 3, 4, 4, 5), true);

        var diffItems = ImmutableList.copyOf(iterator);
        assertEquals(
                List.of(removed(1), removed(1), added(4), added(4), added(5)),
                diffItems
        );
    }

    @Test
    public void testRepeatedElementsWithoutSkip() {
        var iterator = new DiffIterator<>(comparator, Iterators.forArray(1, 1, 2, 3, 3, 3), Iterators.forArray(2, 2, 3, 4, 4, 5), false);

        var diffItems = ImmutableList.copyOf(iterator);
        assertEquals(
                List.of(removed(1), removed(1), added(2), removed(3), removed(3), added(4), added(4), added(5)),
                diffItems
        );
    }

    @Test
    public void testWithRandomNumbersWithSkip() {
        var random = new Random();
        int bound = 1_000_000;
        int sampleSize = bound / 3;
        var oldData = IntStream.generate(() -> random.nextInt(bound)).limit(sampleSize).sorted().boxed().collect(toList());
        var newData = IntStream.generate(() -> random.nextInt(bound)).limit(sampleSize).sorted().boxed().collect(toList());

        var oldDataSet = Set.copyOf(oldData);
        var newDataSet = Set.copyOf(newData);

        var expected = Stream.concat(
                oldData.stream().filter(not(newDataSet::contains)).map(DiffItem::removed),
                newData.stream().filter(not(oldDataSet::contains)).map(DiffItem::added)
        ).sorted(comparing(DiffItem::getValue)).collect(toList());

        var iterator = new DiffIterator<>(comparator, oldData.iterator(), newData.iterator(), true);
        var diffItems = ImmutableList.copyOf(iterator);

        assertEquals(
                expected,
                diffItems
        );
    }

    @Test
    public void testWithRandomNumbersWithoutSkip() {
        var random = new Random();
        int bound = 1_000_000;
        int sampleSize = bound / 3;
        var oldData = IntStream.generate(() -> random.nextInt(bound)).limit(sampleSize).sorted().boxed().collect(toList());
        var newData = IntStream.generate(() -> random.nextInt(bound)).limit(sampleSize).sorted().boxed().collect(toList());

        var oldDataCountMap = oldData.stream().collect(groupingBy(id(), counting()));
        var newDataCountMap = newData.stream().collect(groupingBy(id(), counting()));

        var expected = Sets.union(oldDataCountMap.keySet(), newDataCountMap.keySet()).stream()
                .flatMap(item -> {
                    var oldCnt = oldDataCountMap.getOrDefault(item, 0L).intValue();
                    var newCnt = newDataCountMap.getOrDefault(item, 0L).intValue();
                    return Collections.nCopies(Math.abs(oldCnt - newCnt), newCnt > oldCnt ? added(item) : removed(item)).stream();
                }).sorted(comparing(DiffItem::getValue)).collect(toList());

        var iterator = new DiffIterator<>(comparator, oldData.iterator(), newData.iterator(), false);
        var diffItems = ImmutableList.copyOf(iterator);

        assertEquals(
                expected,
                diffItems
        );
    }

    /**
     * Tests count: 1000. Warm up times: 50.
     * Bound: 1000000. Sample size: 300000.
     * Time: 24.224945875 ± 6.050403092693648 ms
     */
    @Test
    @Ignore("benchmark")
    public void benchmark() {
        var random = new Random();
        var testsCount = 1000;
        var times = new ArrayList<Long>();
        int bound = 1_000_000;
        int sampleSize = 300_000;
        int warmUpTimes = 50;
        for (int i = 0; i < testsCount + warmUpTimes /*warm up*/; i++) {

            var oldData = IntStream.generate(() -> random.nextInt(bound)).limit(sampleSize).sorted().boxed().collect(toList());
            var newData = IntStream.generate(() -> random.nextInt(bound)).limit(sampleSize).sorted().boxed().collect(toList());

            var iterator = new DiffIterator<>(comparator, oldData.iterator(), newData.iterator());
            var start = System.nanoTime();
            while (iterator.hasNext()) {
                iterator.next();
            }
            var end = System.nanoTime();
            if (i >= warmUpTimes) { // after warm up
                times.add(end - start);
            }
            System.gc();
        }

        double avg = times.stream().mapToLong(x -> x).average().orElseThrow();
        double sum = times.stream().mapToDouble(time -> Math.pow(time - avg, 2)).sum();
        double s0 = Math.sqrt(sum / (times.size() - 1));


        System.out.println("Tests count: " + testsCount + ". Warm up times: " + warmUpTimes + ".");
        System.out.println("Bound: " + bound + ". Sample size: " + sampleSize + ".");
        System.out.println("Time: " + avg / 1_000_000 + " ± " + s0 / 1_000_000 + " ms");

    }
}
