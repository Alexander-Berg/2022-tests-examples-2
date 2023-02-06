package ru.yandex.autotests.metrika.appmetrica.matchers;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.beandiffer2.Diff;
import ru.yandex.autotests.irt.testutils.beandiffer2.differ.AbstractDiffer;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.irt.testutils.matchers.NumberApproximatelyEqual.approxEqualTo;

/**
 * Created by konkov on 07.07.2016.
 */
public class DoubleValueDiffer extends AbstractDiffer {
    public static final double DEFAULT_EPSILON = 0.01;

    private final double eps;

    /**
     * @param eps допустимая относительная погрешность.
     */
    public DoubleValueDiffer(double eps) {
        this.eps = eps;
    }

    public DoubleValueDiffer() {
        this(DEFAULT_EPSILON);
    }

    @Override
    public List<Diff> compare(Object actual, Object expected) {
        if (actual == null && expected == null) {
            return emptyList();
        }
        if (actual == null || expected == null) {
            return singletonList(Diff.changed(getField(), Objects.toString(actual), Objects.toString(expected)));
        }

        List<Diff> result = new ArrayList<>();
        Double dExpected = toDouble(expected);
        Matcher<Double> matcher = approxEqualTo(dExpected).withDifferenceInPercents(eps * 100);
        if (!matcher.matches(actual)) {
            result.add(Diff.changed(getField(), actual, matcher.toString()));
        }
        return result;
    }

    private Double toDouble(Object value) {
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }

        throw new IllegalStateException("Double value differ does'nt make sense for " + value.getClass().getSimpleName());
    }
}
