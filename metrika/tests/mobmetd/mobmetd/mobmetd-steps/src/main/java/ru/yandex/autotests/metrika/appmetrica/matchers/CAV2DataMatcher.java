package ru.yandex.autotests.metrika.appmetrica.matchers;

import java.lang.reflect.InvocationTargetException;

import org.apache.commons.beanutils.PropertyUtils;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import static java.lang.String.format;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;

/**
 * Created by graev on 30/01/2017.
 */
public final class CAV2DataMatcher<T> extends TypeSafeMatcher<T>{
    private final Matcher<?> dataMatcher;
    private Throwable matchingException;

    private CAV2DataMatcher(Matcher<?> dataMatcher) {
        this.dataMatcher = dataMatcher;
    }

    @Override
    protected boolean matchesSafely(T item) {
        boolean result;

        try {
            result = dataMatcher.matches(getTotals(item));
        } catch (Throwable e) {
            result = false;
            matchingException = e;
        }

        return result;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("total is ")
                .appendDescriptionOf(dataMatcher);
    }

    @Override
    protected void describeMismatchSafely(T item, Description mismatchDescription) {
        if (matchingException == null) {
            try {
                mismatchDescription.appendText(format("data is %sempty", getTotals(item) == 0L ? EMPTY : "not "));
            } catch (Throwable e) {
                mismatchDescription.appendText("exception while describing mismatch ")
                        .appendValue(e);
            }
        } else {
            mismatchDescription.appendText("exception while matching ")
                    .appendValue(matchingException);
        }
    }

    private Long getTotals(T item) throws IllegalAccessException, InvocationTargetException, NoSuchMethodException {
        return (Long) PropertyUtils.getProperty(PropertyUtils.getProperty(item, "totals"), "cohortSize");
    }

    public static Matcher<?> expectNotEmptyCA() {
        return new CAV2DataMatcher<>(not(equalTo(0L)));
    }

}
