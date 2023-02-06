package ru.yandex.autotests.metrika.matchers;

import org.apache.commons.lang3.ObjectUtils;
import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;

import java.util.List;
import java.util.Objects;

import static com.google.common.primitives.Ints.min;
import static org.apache.commons.collections4.CollectionUtils.isEmpty;

/**
 * Created by okunev on 24.12.2014.
 * <p/>
 * Матчер для сравнения пересекающихся частей двумерных массивов.
 */
public class TwoDimensionalArrayMatcher<T> extends TypeSafeMatcher<List<List<T>>> {

    private final List<List<T>> expected;

    private int unequalI = -1;
    private int unequalJ = -1;

    public TwoDimensionalArrayMatcher(List<List<T>> expected) {
        this.expected = expected;
    }

    @Override
    protected boolean matchesSafely(List<List<T>> actual) {
        if (isEmpty(actual) || isEmpty(expected)) {
            return false;
        }

        for (int i = 0; i < min(actual.size(), expected.size()); i++) {
            unequalI = i;

            if (isEmpty(actual.get(i))) {
                return false;
            }

            for (int j = 0; j < min(actual.get(i).size(), expected.get(i).size()); j++) {
                if (!Objects.equals(actual.get(i).get(j), expected.get(i).get(j))) {
                    unequalJ = j;
                    return false;
                }
            }
        }

        return true;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Значения пересекающихся частей массивов должны совпадать.");
    }

    @Override
    public void describeMismatchSafely(final List<List<T>> actual, final Description description) {
        if (unequalI < 0) {
            description.appendText(String.format("Массив %s пустой.",
                    isEmpty(actual) ? "actual" : "expected"));
        } else if (unequalJ < 0) {
            description.appendText(String.format("Строка %s массива actual пустая.", unequalI));
        } else {
            description.appendText(String.format("В строке %s, столбце %s вместо '%s' было '%s'.",
                    unequalI,
                    unequalJ,
                    expected.get(unequalI).get(unequalJ),
                    actual.get(unequalI).get(unequalJ)));
        }
    }

    /**
     * @param expected ожидаемые элементы массива
     * @param <S>      тип элементов массива
     * @return матчер для проверки каждой строки двумерного массива на содержание элементов строк другого массива
     */
    public static <S> TwoDimensionalArrayMatcher<S> everyRowStartsWithRowOf(List<List<S>> expected) {
        return new TwoDimensionalArrayMatcher<>(expected);
    }

}
