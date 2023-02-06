package ru.yandex.autotests.metrika.matchers;

import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.util.List;

import static org.apache.commons.lang3.StringUtils.isEmpty;

/**
 * Created by konkov on 04.09.2014.
 * Матчер для сравнения списков направлений сортировки.
 * Учитывает, что "+" перед наименованием поля (метрика, измерение) может быть опущен.
 */
public class SortMatcher extends TypeSafeMatcher<List<String>> {

    private static final String DESCENDING_SORT_DIRECTION = "-";
    private static final String ASCENDING_SORT_DIRECTION = "+";

    private final String[] expected;

    public SortMatcher(String expected) {
        if (!isEmpty(expected)) {
            this.expected = expected.split(",");
        }
        else {
            this.expected = ArrayUtils.EMPTY_STRING_ARRAY;
        }
    }

    private static Pair<String, String> getSortDirectionAndField(String sort) {
        if (sort.startsWith(DESCENDING_SORT_DIRECTION))
            return Pair.of(DESCENDING_SORT_DIRECTION, sort.substring(1, sort.length()));
        else {
            if (sort.startsWith(ASCENDING_SORT_DIRECTION)) {
                return Pair.of(ASCENDING_SORT_DIRECTION, sort.substring(1, sort.length()));
            }
            return Pair.of(ASCENDING_SORT_DIRECTION, sort);
        }
    }

    /**
     * Создает матчер, который проверят эквивалентность сортировки.
     *
     * @param expected ожидаемая сортировка, на эквивалентность которой и выполняется проверка,
     *                 учитывается, что "+" перед наименованием метрики или измерения может быть опущен.
     */
    public static Matcher<List<String>> isSortEqualTo(String expected) {
        return new SortMatcher(expected);
    }

    private boolean areEqual(String actualSort, String expectedSort) {
        Pair<String, String> actual = getSortDirectionAndField(actualSort);
        Pair<String, String> expected = getSortDirectionAndField(expectedSort);

        return actual.equals(expected);
    }

    @Override
    protected boolean matchesSafely(List<String> strings) {
        if (strings.size() == expected.length) {
            boolean result = true; //предположение
            for (int i = 0; i < expected.length; i++) {
                result = result && areEqual(strings.get(i), expected[i]);
            }
            return result;
        } else {
            return false;
        }
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("ожидаемая сортировка")
                .appendValueList("[ ", ", ", " ]", expected);
    }
}
