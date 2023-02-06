package ru.yandex.autotests.internalapid.util;

import java.util.Random;

public class DataUtil {
    private static Random rnd = new Random();
    public static String getRandomCounterName() {
        return "Тестовый счётчик Метрики " + rnd.nextInt();
    }
}
