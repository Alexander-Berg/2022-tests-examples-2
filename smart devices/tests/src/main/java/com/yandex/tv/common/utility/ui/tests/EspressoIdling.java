package com.yandex.tv.common.utility.ui.tests;

/**
 * Added a sleep statement to match the app's execution delay.
 * The recommended way to handle such scenarios is to use Espresso idling resources:
 * https://google.github.io/android-testing-support-library/docs/espresso/idling-resource/index.html
 */

public class EspressoIdling {

    public static void sleepStatement(int millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
