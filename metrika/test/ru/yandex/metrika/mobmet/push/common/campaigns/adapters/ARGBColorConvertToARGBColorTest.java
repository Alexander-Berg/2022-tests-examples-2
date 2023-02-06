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
public class ARGBColorConvertToARGBColorTest {

    @Parameter
    public String argbColor;

    @Parameter(1)
    public Integer expectedColorAsInt;

    @Parameters(name = "{0}, {1}")
    public static Collection<Object[]> getParams() {
        return Arrays.asList(
                new Object[]{"#00FFFFFF", 16777215},
                new Object[]{"#0000FFFF", 65535},
                new Object[]{"#000000FF", 255},
                new Object[]{"#0F0F0F0F", 252645135},
                new Object[]{"#FFFFFFFF", -1},
                new Object[]{"#00000005", 5}
        );
    }

    @Test
    public void convertARGBColor() {
        assertEquals(
                argbColor.toLowerCase(),
                ARGBColor.convertToARGBColor(expectedColorAsInt).orElseThrow(IllegalArgumentException::new).toLowerCase()
        );
    }
}
