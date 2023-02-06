package ru.yandex.autotests.metrika.matchers;

import ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher;

import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;

public class CounterMatchers {
    public static <T> BeanDifferMatcher<T> beanEquivalentIgnoringFeatures(T expectedBean) {
        return BeanDifferMatcher.beanEquivalent(expectedBean).fields(ignore("features"));
    }
}
