package ru.yandex.metrika.userparams2d.steps;

import java.util.List;
import java.util.Random;

import static java.util.Arrays.asList;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomUInt32;

public class TestCountersProvider {
    // эти счетчики инсертятся в тестовую табличку counters в mysql_dumps
    private static final List<Integer> bigCounters = asList(1, 2, 3);
    private static final List<Integer> smallCounters = asList(4, 5, 6);

    private static final Random random = new Random(0);


    public static int getRandomBigCounter() {
        return bigCounters.get((int) (getRandomUInt32(random) % bigCounters.size()));
    }

    public static int getRandomSmallCounter() {
        return smallCounters.get((int) (getRandomUInt32(random) % smallCounters.size()));
    }

    public static boolean isBig(int counterId) {
        return bigCounters.contains(counterId);
    }

    public static List<Integer> getBigCounters() {
        return bigCounters;
    }

    public static List<Integer> getSmallCounters() {
        return smallCounters;
    }
}
