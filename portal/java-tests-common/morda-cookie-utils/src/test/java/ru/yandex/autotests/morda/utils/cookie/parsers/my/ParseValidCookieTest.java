package ru.yandex.autotests.morda.utils.cookie.parsers.my;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * User: leonsabr
 * Date: 24.06.12
 */
@RunWith(Parameterized.class)
public class ParseValidCookieTest {
    private static final Map<String, Map<String, List<String>>> DATA =
            new HashMap<String, Map<String, List<String>>>() {{
                put("YycCAAbIAeAPQkAA", new HashMap<String, List<String>>() {{
                    put("200", new ArrayList<String>() {{
                        add("1000000");
                    }});
                    put("39", new ArrayList<String>() {{
                        add("0");
                        add("6");
                    }});
                }});

                put("YyMCAwUnAgABLgEBAA==", new HashMap<String, List<String>>() {{
                    put("35", new ArrayList<String>() {{
                        add("3");
                        add("5");
                    }});
                    put("39", new ArrayList<String>() {{
                        add("0");
                        add("1");
                    }});
                    put("46", new ArrayList<String>() {{
                        add("1");
                    }});
                }});

                put("YycCAAFFAYgBAA==", new HashMap<String, List<String>>() {{
                    put("39", new ArrayList<String>() {{
                        add("0");
                        add("1");
                    }});
                    put("69", new ArrayList<String>() {{
                        add("2049");
                    }});
                }});

                put("", new HashMap<String, List<String>>());
            }};
    String my;

    public ParseValidCookieTest(String my) {
        this.my = my;
    }

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        Object[][] data = new Object[DATA.size()][1];
        int i = 0;
        for (String my : DATA.keySet()) {
            data[i++][0] = my;
        }
        return Arrays.asList(data);
    }

    @Test
    public void checkParserConsistency() {
        assertThat(MyCookieParser.parse(my), equalTo(DATA.get(my)));
    }
}
