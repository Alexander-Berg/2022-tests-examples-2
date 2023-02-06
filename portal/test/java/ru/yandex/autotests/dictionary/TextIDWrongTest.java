package ru.yandex.autotests.dictionary;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import java.util.Arrays;
import java.util.Collection;

/**
 * User: leonsabr
 * Date: 27.07.12
 */
@RunWith(Parameterized.class)
public class TextIDWrongTest {
    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        String[] values = {null, "", "a"};
        int len = values.length;
        Object[][] data = new Object[len * len * len - 1][len];
        for (int i = 0; i < len; i++) {
            for (int j = 0; j < len; j++) {
                for (int k = 0; k < len; k++) {
                    if (values[i] != null && !values[i].isEmpty() && values[j] != null
                            && !values[j].isEmpty() && values[k] != null && !values[k].isEmpty()) {
                        continue;
                    }
                    data[i * len * len + j * len + k] = new Object[]{values[i], values[j], values[k]};
                }
            }
        }
        return Arrays.asList(data);
    }

    private String first;
    private String second;
    private String third;

    public TextIDWrongTest(String first, String second, String third) {
        this.first = first;
        this.second = second;
        this.third = third;
    }

    @Test(expected = IllegalArgumentException.class)
    public void checkArguments() {
        new TextID(first, second, third);
    }
}
