package ru.yandex.autotests.mordacommonsteps.utils;

/**
 * User: eoff
 * Date: 15.02.13
 */
public class TestFailedFlag {
    private static boolean isFailed = false;

    public static boolean notFailed() {
        return !isFailed;
    }

    public static void setFailed(boolean failed) {
        isFailed = failed;
    }
}
