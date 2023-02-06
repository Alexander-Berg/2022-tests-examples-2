package ru.yandex.autotests.metrika.matchers;

import org.apache.commons.lang3.ArrayUtils;
import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.metrika.api.constructor.response.ComparisonData;

import java.util.Objects;

/**
 * Created by konkov on 28.10.2014.
 *
 * Матчер для проверки совпадения двух сравниваемых сегментов
 */
public class ComparisonDataObjectMatcher extends TypeSafeMatcher<ComparisonData> {

    @Override
    protected boolean matchesSafely(ComparisonData item) {
        return Objects.deepEquals(item.getA(), item.getB());
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("значения метрик должны совпадать");
    }

    /**
     * @return матчер, который проверяет, что в сравниваемых сегментах значения метрик одинаковы.
     */
    public static ComparisonDataObjectMatcher noDifference() {
        return new ComparisonDataObjectMatcher();
    }
}
