package ru.yandex.metrika.segments.core.query.paramertization;

/**
 * значения для квантилей.
 * Created by orantius on 4/24/15.
 */
public final class Qvalue {

    private Qvalue() {
    }

    public static int[] quantileValues() {
        return new int[] {50, 75, 90, 95, 99};
    }

}
