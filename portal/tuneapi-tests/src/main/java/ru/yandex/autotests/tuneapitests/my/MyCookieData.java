package ru.yandex.autotests.tuneapitests.my;

import java.util.Arrays;
import java.util.List;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class MyCookieData {
    public static final List<String> ALL_USED_MY_BLOCKS = Arrays.asList(
            "1", "5", "7", "8", "12", "14", "16", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35",
            "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56",
            "57", "58", "59"
    );

    public static final List<String> MY_BLOCKS = Arrays.asList(
            "1", "5", "26", "38", "39", "40", "41", "54", "59", "213"
    );

    public static final List<List<String>> MY_PARAMS = Arrays.asList(
            Arrays.asList("1"),
            Arrays.asList("8", "120"),
            Arrays.asList("358"),
            Arrays.asList("16300"),
            Arrays.asList("200000000"),
            Arrays.asList("1234", "344", "3355", "12", "9033")
    );

    public static final List<List<String>> BAD_PARAMS = Arrays.asList(
            Arrays.asList(""),
            Arrays.asList("r", "e"),
            Arrays.asList("2.33"),
            Arrays.asList("4,3"),
            Arrays.asList("999990000000"),
            Arrays.asList("-1234", "+344", "3355", "12", "9033")
    );

    public static final List<String> BAD_BLOCKS = Arrays.asList(
            "", "-5", "s", "dd", "39.2", "40,2", "-", "54+"
    );
}
