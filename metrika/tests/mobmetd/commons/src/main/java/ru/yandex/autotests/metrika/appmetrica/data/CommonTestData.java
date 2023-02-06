package ru.yandex.autotests.metrika.appmetrica.data;

import org.apache.commons.lang3.RandomUtils;
import org.apache.commons.lang3.StringUtils;

import static org.apache.commons.lang3.RandomUtils.nextInt;

public class CommonTestData {

    private static final int MAX_COLOR_SIZE = 8;
    private static final int COLOR_POSITION_SIZE = 2;
    private static final String PLACEHOLDER = "0";

    public static String randomColor() {
        return randomColor(RandomUtils.nextBoolean());
    }

    public static String randomColor(boolean withAlpha) {
        String hexInt = Integer.toHexString(nextInt()).toUpperCase();

        if (hexInt.length() < MAX_COLOR_SIZE) {
            hexInt = StringUtils.repeat(PLACEHOLDER, MAX_COLOR_SIZE - hexInt.length()) + hexInt;
        }

        return "#" + (withAlpha ? hexInt : hexInt.substring(COLOR_POSITION_SIZE));
    }
}
