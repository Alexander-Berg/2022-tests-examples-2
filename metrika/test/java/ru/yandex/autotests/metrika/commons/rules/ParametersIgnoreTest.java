package ru.yandex.autotests.metrika.commons.rules;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import java.util.Collection;
import java.util.function.Predicate;

import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.anything;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.metrika.commons.rules.ObjectParam.param;

/**
 * Created by konkov on 18.12.2015.
 */
@RunWith(Parameterized.class)
public class ParametersIgnoreTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameter(0)
    public Integer valueParam;

    @Parameterized.Parameter(1)
    public String stringParam;

    @Parameterized.Parameter(2)
    public ObjectParam objectParam;

    @Parameterized.Parameters(name = "{0} {1} {2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {0, "A1", param("1Z")},
                {0, "B1", param("2Z")},
                {0, "C1", param("3Z")},
                {0, "D1", param("4Z")},
        });
    }

    @Test
    @IgnoreParameters(reason = "Игнорируем по значению параметра", tag = "equals")
    @IgnoreParameters(reason = "Игнорируем по строковому представлению", tag = "string")
    @IgnoreParameters(reason = "Игнорируем по матчеру", tag = "hamcrest matcher")
    @IgnoreParameters(reason = "Игнорируем по предикату", tag = "lambda")
    public void shouldBeIgnored() {
        assertThat("This should be ignored", false);
    }

    @IgnoreParameters.Tag(name = "equals")
    public static Collection<Object[]> ignoreParametersEquals() {
        return asList(new Object[][]{
                {0, "A1", param("1Z")}
        });
    }

    @IgnoreParameters.Tag(name = "string")
    public static Collection<Object[]> ignoreParametersString() {
        return asList(new Object[][]{
                {"0", "B1", "2Z"},
        });
    }

    @IgnoreParameters.Tag(name = "hamcrest matcher")
    public static Collection<Object[]> ignoreParametersMatcher() {
        return asList(new Object[][]{
                {anything(), startsWith("C"), equalTo(param("3Z"))},
        });
    }

    @IgnoreParameters.Tag(name = "lambda")
    public static Collection<Object[]> ignoreParametersPredicate() {
        return asList(new Object[][]{
                {
                        (Predicate<Integer>) i -> i.equals(0),
                        (Predicate<String>) s -> s.equals("D1"),
                        (Predicate<ObjectParam>) p -> p.getValue().equals("4Z")
                },
        });
    }
}
