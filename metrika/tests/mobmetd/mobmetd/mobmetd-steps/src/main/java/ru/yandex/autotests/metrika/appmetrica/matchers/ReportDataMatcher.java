package ru.yandex.autotests.metrika.appmetrica.matchers;

import org.apache.commons.beanutils.PropertyUtils;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.lang.reflect.InvocationTargetException;
import java.util.List;

import static java.lang.String.format;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;

/**
 * Created by konkov on 31.07.2015.
 * <p/>
 * Матчер для проверки количетсва строк в отчете
 */
public class ReportDataMatcher<T> extends TypeSafeMatcher<T> {

    private final Matcher<List> dataMatcher;
    private Throwable matchingException;

    public ReportDataMatcher(Matcher<List> dataMatcher) {
        this.dataMatcher = dataMatcher;
    }

    @Override
    protected boolean matchesSafely(T item) {
        boolean result;

        try {
            result = dataMatcher.matches(getData(item));
        } catch (Throwable e) {
            result = false;
            matchingException = e;
        }

        return result;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("data is ")
                .appendDescriptionOf(dataMatcher);
    }

    @Override
    protected void describeMismatchSafely(T item, Description mismatchDescription) {
        if (matchingException == null) {
            try {
                mismatchDescription.appendText(format("data is %sempty", getData(item).size() == 0 ? EMPTY : "not "));
            } catch (Throwable e) {
                mismatchDescription.appendText("exception while describing mismatch ")
                        .appendValue(e);
            }
        } else {
            mismatchDescription.appendText("exception while matching ")
                    .appendValue(matchingException);
        }
    }

    private List getData(T item) throws IllegalAccessException, InvocationTargetException, NoSuchMethodException {
        return (List) PropertyUtils.getProperty(item, "data");
    }

    public static Matcher expectNotEmptyReport() {
        return new ReportDataMatcher(not(empty()));
    }
}
