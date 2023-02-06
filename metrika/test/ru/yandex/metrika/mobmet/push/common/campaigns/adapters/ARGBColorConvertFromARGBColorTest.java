package ru.yandex.metrika.mobmet.push.common.campaigns.adapters;

import java.util.Arrays;
import java.util.Collection;
import java.util.Optional;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class ARGBColorConvertFromARGBColorTest {

    @Parameter
    public String argbColor;

    @Parameter(1)
    public Integer expectedColorAsInt;

    @Parameters(name = "0")
    public static Collection<Object[]> getParams() {
        return Arrays.asList(
                new Object[]{"#00FFFFFF", 16777215},
                new Object[]{"#0000FFFF", 65535},
                new Object[]{"#000000FF", 255},
                new Object[]{"#0F0F0F0F", 252645135},
                new Object[]{"#FFFFFFFF", -1},
                new Object[]{"#FFFFFF", -1},
                new Object[]{"#00FFFF", -16711681},
                new Object[]{"#0000FF", -16776961},
                new Object[]{"#0F0F0F", -15790321}
        );
    }

    @Test
    public void convertARGBColor() {
        assertEquals(
                ARGBColor.convertFromARGBColor(argbColor).orElseThrow(IllegalArgumentException::new),
                expectedColorAsInt
        );
    }

    @Test
    public void convertNull() {
        assertEquals(ARGBColor.convertFromARGBColor(null), Optional.empty());
    }
}
