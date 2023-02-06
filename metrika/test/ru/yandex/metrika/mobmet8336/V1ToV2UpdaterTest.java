package ru.yandex.metrika.mobmet8336;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet8336.data.Segment;
import ru.yandex.metrika.util.io.IOUtils;

@RunWith(Parameterized.class)
@Ignore
public class V1ToV2UpdaterTest {

    @Parameterized.Parameter
    public String testName;

    @Parameterized.Parameters(name = "type: {0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[][]{
                        {"test1"},
                        {"test2"},
                        {"test3"},
                        {"test4"},
                        {"test5"},
                        {"test6"},
                        {"test7"},
                        {"test8"},
                        {"test9"},
                        {"test10"},
                        {"test11"},
                }
        );
    }

    @Test
    public void update() {
        String oldParams = IOUtils.resourceAsString(V1ToV2UpdaterTest.class, testName + "/input.json");
        String newParams = IOUtils.resourceAsString(V1ToV2UpdaterTest.class, testName + "/output.json");
        Segment newSegment = new V1ToV2Updater().convert(new Segment(1, "0", oldParams, null, "", 0));
        Assert.assertEquals(removeFormatting(newParams), newSegment.getParams2());
    }

    private static String removeFormatting(String str) {
        String result = "";
        for (String line : str.split("\\n")) {
            String trimmed = line.trim();
            if (trimmed.isEmpty()) {
                continue;
            }
            result += trimmed;
        }
        return result.replaceAll(": ", ":");
    }
}
