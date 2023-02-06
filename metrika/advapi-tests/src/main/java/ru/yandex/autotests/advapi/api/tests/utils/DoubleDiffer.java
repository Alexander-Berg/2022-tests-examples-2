package ru.yandex.autotests.advapi.api.tests.utils;

import org.hamcrest.Matcher;
import org.hamcrest.number.IsCloseTo;
import ru.yandex.autotests.irt.testutils.beandiffer.diff.Diff;
import ru.yandex.autotests.irt.testutils.beandiffer.differ.Differ;
import ru.yandex.autotests.irt.testutils.beandiffer.differ.MatcherDiffer;

import static org.hamcrest.CoreMatchers.equalTo;

public class DoubleDiffer extends Differ<Double> {

    private double accuracy;

    public DoubleDiffer(double accuracy) {
        this.accuracy = accuracy;
    }

    @Override
    public boolean accepts(final Class type) {
        return Number.class.isAssignableFrom(type);
    }

    @Override
    public Diff compare(Double expected, Double actual) {
        Matcher<Double> matcher = isInvalid(expected) || isInvalid(actual) ? equalTo(expected) : IsCloseTo.closeTo(expected, accuracy);
        Differ<Double> differ = new MatcherDiffer<Double>(matcher).withFieldPath(fieldPath);
        return differ.compare(expected, actual);
    }

    private boolean isInvalid(Double value) {
        return value.isInfinite() || value.isNaN();
    }

}
