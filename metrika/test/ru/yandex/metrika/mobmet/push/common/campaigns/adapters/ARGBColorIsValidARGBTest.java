package ru.yandex.metrika.mobmet.push.common.campaigns.adapters;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class ARGBColorIsValidARGBTest {

    @Parameter
    public String argbColor;

    @Parameter(1)
    public boolean expectedIsValid;

    @Parameters(name = "{0}")
    public static Collection<Object[]> getParams() {
        return Arrays.asList(
                new Object[]{"", false},
                new Object[]{"#FF", false},
                new Object[]{"#FF00FF", true},
                new Object[]{"#FF00FF0", false},
                new Object[]{"#FF00FF00", true},
                new Object[]{"#FF00FF00FF", false},
                new Object[]{"#XXYYXX", false},
                new Object[]{"FF00FF", false}
        );
    }


    @Test
    public void isValidARGBString() {
        assertEquals(expectedIsValid, ARGBColor.isValidARGBString(argbColor));
    }
}
