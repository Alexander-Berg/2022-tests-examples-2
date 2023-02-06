package ru.yandex.autotests.metrika.tests.utils;

import org.hamcrest.Matcher;

import ru.yandex.autotests.irt.testutils.beandiffer.diff.Diff;
import ru.yandex.autotests.irt.testutils.beandiffer.differ.Differ;
import ru.yandex.autotests.irt.testutils.beandiffer.differ.MatcherDiffer;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.metrika.matchers.Matchers.closeTo;

public class DoubleDiffer extends Differ<Double> {

    private final double accuracy;
    private final boolean relative;

    public DoubleDiffer(double accuracy) {
        this(accuracy, false);
    }

    public DoubleDiffer(double accuracy, boolean relative) {
        this.accuracy = accuracy;
        this.relative = relative;
    }

    @Override
    public boolean accepts(final Class type) {
        return Number.class.isAssignableFrom(type);
    }

    @Override
    public Diff compare(Double expected, Double actual) {
        Matcher<Double> matcher = isInvalid(expected) || isInvalid(actual) ? equalTo(expected) : closeTo(expected, accuracy, relative);
        Differ<Double> differ = new MatcherDiffer<Double>(matcher).withFieldPath(fieldPath);
        return differ.compare(expected, actual);
    }

    private boolean isInvalid(Double value) {
        return value.isInfinite() || value.isNaN();
    }

}
