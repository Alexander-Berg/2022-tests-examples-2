package ru.yandex.metrika.segments.core.query.filter;

import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;

/**
 * Created by graev on 06/04/2017.
 */
@RunWith(Parameterized.class)
public class CompoundAndUnparsedTest {

    public static final String[] STR = {};

    @Parameterized.Parameter
    public List<String> argumentsList;

    public String[] arguments;

    @Parameterized.Parameter(1)
    public String expected;

    @Parameterized.Parameters(name = "AndUnparsed{0} = {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                param(of(), ""),
                param(of(""), ""),
                param(of("", ""), ""),
                param(of("A"), "A"),
                param(of("A", ""), "A"),
                param(of("A", "B"), "(A) AND (B)"),
                param(of("A", "", "B"), "(A) AND (B)")
        );
    }

    @Before
    public void setup() {
        arguments = argumentsList.toArray(STR);
    }

    @Test
    public void testAndUnparsed() {
        assertThat(Compound.andUnparsed(arguments), equalTo(expected));
    }


    public static Object[] param(List<String> arguments, String result) {
        return new Object[]{arguments, result};
    }
}
