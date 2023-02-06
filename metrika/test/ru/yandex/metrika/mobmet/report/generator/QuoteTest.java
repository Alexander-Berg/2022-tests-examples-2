package ru.yandex.metrika.mobmet.report.generator;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class QuoteTest {

    @Parameterized.Parameter
    public String input;
    @Parameterized.Parameter(1)
    public String expected;

    @Test
    public void testQuote() {
        assertEquals(expected, ReportParamGenerationUtils.quote(input));
    }


    @Parameterized.Parameters(name = "Params: {0}, report type: {1}")
    public static Collection<Object[]> init() {
        return ImmutableList.<Object[]>builder()
                .add(params("abc", "'abc'"))
                .add(params("'", "'\\''"))
                .add(params("\\'", "'\\\\\\''"))
                .add(params("/'\\", "'/\\'\\\\'"))
                .add(params("\\\\'", "'\\\\\\\\\\''"))
                .add(params("text \\ or '", "'text \\\\ or \\''"))
                .add(params("test (\")", "'test (\")'"))
                .add(params("alcatel \\t new", "'alcatel \\\\t new'"))
                .build();
    }

    private static Object[] params(Object... params) {
        return params;
    }
}
