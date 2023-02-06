package ru.yandex.metrika.expenses;

import java.util.Collection;
import java.util.List;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static java.util.List.of;
import static java.util.stream.Collectors.toList;
import static ru.yandex.metrika.expenses.ExpenseUtils.splitByDays;

@RunWith(Parameterized.class)
public class ExpenseUtilsTest {

    @Parameterized.Parameter
    public int value;

    @Parameterized.Parameter(1)
    public int daysAmount;

    @Parameterized.Parameter(2)
    public List<Integer> expected;

    @Parameterized.Parameters(name = "value {0}, daysAmount {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                of(0, 0, of()),
                of(0, 1, of(0)),
                of(1, 1, of(1)),
                of(2, 2, of(1, 1)),
                of(4, 2, of(2, 2)),
                of(3, 2, of(2, 1)),
                of(5, 2, of(3, 2)),
                of(3, 3, of(1, 1, 1)),
                of(9, 3, of(3, 3, 3)),
                of(4, 3, of(1, 2, 1)),
                of(5, 3, of(2, 1, 2)),
                of(7, 13, of(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1)),
                of(19, 7, of(3, 2, 3, 3, 3, 2, 3)),
                of(997, 31, of(32, 32, 32, 33, 32, 32, 32, 32, 32, 33, 32, 32, 32, 32, 32, 33, 32, 32, 32, 32, 32, 33, 32, 32, 32, 32, 32, 33, 32, 32, 32))
        ).stream().map(List::toArray).collect(toList());
    }

    @Test
    public void testIntExpected() {
        Assert.assertEquals(expected, splitByDays(value, daysAmount));
    }

    @Test
    public void testIntSum() {
        Assert.assertEquals(value, splitByDays(value, daysAmount).stream().mapToInt(i -> i).sum());
    }

    @Test
    public void testIntExpectedInverse() {
        Assert.assertEquals(expected.stream().map(i -> -i).collect(toList()), splitByDays(-value, daysAmount));
    }

    @Test
    public void testIntSumInverse() {
        Assert.assertEquals(-value, splitByDays(value, daysAmount).stream().mapToInt(i -> -i).sum());
    }


    @Test
    public void testLongExpected() {
        Assert.assertEquals(expected.stream().map(i -> (long) i).collect(toList()), splitByDays((long) value, daysAmount));
    }

    @Test
    public void testLongSum() {
        Assert.assertEquals((long) value, splitByDays((long) value, daysAmount).stream().mapToLong(i -> i).sum());
    }

    @Test
    public void testLongExpectedInverse() {
        Assert.assertEquals(expected.stream().map(i -> (long) -i).collect(toList()), splitByDays((long) -value, daysAmount));
    }

    @Test
    public void testLongSumInverse() {
        Assert.assertEquals((long) -value, splitByDays((long) value, daysAmount).stream().mapToLong(i -> -i).sum());
    }
}
