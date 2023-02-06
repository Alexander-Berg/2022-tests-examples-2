package ru.yandex.autotests.metrika.matchers;

import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.collections4.ListUtils;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.matchers.TwoDimensionalArrayMatcher.everyRowStartsWithRowOf;

/**
 * Created by okunev on 04.02.2015.
 */
public class TwoDimensionalArrayMatcherTest {

    List<List<Integer>> nullArray = null;

    List<List<Integer>> arrayWithNull = new ArrayList<List<Integer>>() {{
        add(asList(1, 2));
        add(null);
    }};

    List<List<Integer>> arrayOfArrayOfNull = asList(asList((Integer) null));

    List<List<Integer>> emptyArray = new ArrayList<>();

    List<List<Integer>> array2by2 = asList(
            asList(1, 2),
            asList(3, 4));

    List<List<Integer>> array3by3 = asList(
            asList(1, 2, 2),
            asList(3, 4, 4),
            asList(5, 6, 6));

    List<List<Integer>> arrayWithEmptyRows = asList(
            (List<Integer>) new ArrayList<Integer>(),
            (List<Integer>) new ArrayList<Integer>(),
            (List<Integer>) new ArrayList<Integer>());

    @Test
    public void lesserToBiggerMatchTest() {
        assertThat(array2by2, everyRowStartsWithRowOf(array3by3));
    }

    @Test
    public void biggerToLesserMatchTest() {
        assertThat(array3by3, everyRowStartsWithRowOf(array2by2));
    }

    @Test(expected = AssertionError.class)
    public void actualNullArrayTest() {
        assertThat(nullArray, everyRowStartsWithRowOf(array2by2));
    }

    @Test(expected = AssertionError.class)
    public void expectedNullArrayTest() {
        assertThat(array2by2, everyRowStartsWithRowOf(nullArray));
    }

    @Test(expected = AssertionError.class)
    public void arrayWithNullTest() {
        assertThat(arrayWithNull, everyRowStartsWithRowOf(array2by2));
    }

    @Test(expected = AssertionError.class)
    public void arrayOfArrayOfNullTest() {
        assertThat(arrayOfArrayOfNull, everyRowStartsWithRowOf(array2by2));
    }

    @Test(expected = AssertionError.class)
    public void emptyArrayTest() {
        assertThat(emptyArray, everyRowStartsWithRowOf(array2by2));
    }

    @Test
    public void emptyRowsTest() {
        assertThat(array3by3, everyRowStartsWithRowOf(arrayWithEmptyRows));
    }

}
