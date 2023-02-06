package ru.yandextaxi.argument;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandextaxi.DateUtils;

import java.util.Arrays;
import java.util.Collection;

@RunWith(Parameterized.class)
public class DateVerifierTest {
    private static final boolean VALID = true;
    private static final boolean WRONG = false;

    @Parameterized.Parameters(name = "{0} valid: {1}")
    public static Collection<Object[]> data() {
        return Arrays.asList(new Object[][] {
                { "2018-03",  VALID },
                { "2018-12",  VALID },
                { "2018-01",  VALID },
                { "2008-01",  VALID },
                { "2000-01",  VALID },
                { "3210-07",  VALID },
                { "2018-1",   WRONG },
                { "2018-13",  WRONG },
                { "2018-00",  WRONG },
                { "2018-30",  WRONG },
                { "20018-04", WRONG },
                { "1990-12",  WRONG },
                { "12 dec",   WRONG },
                { "2018 03",  WRONG },
                { "20-18-03", WRONG },
                { "04-2018",  WRONG },
                { "4-2018",   WRONG },
                { "04-18",    WRONG },
                { "",         WRONG },
        });
    }

    private String inputString;
    private boolean expected;

    public DateVerifierTest(String inputString, boolean expected) {
        this.inputString = inputString;
        this.expected = expected;
    }

    @Test
    public void testValidate() {
        boolean result = DateUtils.verifyDateFormat(inputString);
        Assert.assertEquals(result, this.expected);
    }
}
