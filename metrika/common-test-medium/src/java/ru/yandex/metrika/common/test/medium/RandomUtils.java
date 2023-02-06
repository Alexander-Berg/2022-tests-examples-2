package ru.yandex.metrika.common.test.medium;

import java.math.BigInteger;
import java.util.Random;

import org.apache.commons.lang.RandomStringUtils;
import org.joda.time.DateTime;

public class RandomUtils {

    private static final int INT8_LIMIT = (1 << 7) - 1;
    private static final int U_INT8_LIMIT = (1 << 8) - 1;
    private static final int U_INT16_LIMIT = (1 << 16) - 1;
    private static final long U_INT32_LIMIT = (1L << 32) - 1;
    private static final int U_INT64_BITS = 64;
    private static final int SHORT_STRING_LENGTH = 3;
    private static final int STRING_LENGTH = 7;

    public static Integer getRandomInt8(Random random) {
        return random.nextInt(U_INT8_LIMIT) - INT8_LIMIT - 1;
    }

    public static Integer getRandomUInt8(Random random) {
        return random.nextInt(U_INT8_LIMIT);
    }

    public static Integer getRandomUInt16(Random random) {
        return random.nextInt(U_INT16_LIMIT);
    }

    public static Integer getRandomInt32(Random random) {
        return random.nextInt();
    }

    public static Long getRandomUInt32(Random random) {
        return (long) (random.nextDouble() * U_INT32_LIMIT);
    }

    public static Long getRandomLimitedUInt32(Random random, long limit) {
        return (long) (random.nextDouble() * limit);
    }

    public static Long getRandomLimitedInt64(Random random, long limit) {
        return (long) (random.nextDouble() * limit * 2) - limit;
    }

    public static BigInteger getRandomUInt64(Random random) {
        return new BigInteger(U_INT64_BITS, random).abs();
    }

    public static Float getRandomFloat(Random random) {
        return random.nextFloat();
    }

    public static Boolean getRandomBoolean(Random random) {
        return random.nextBoolean();
    }

    public static String getRandomShortString(Random random) {
        return getRandomString(random, SHORT_STRING_LENGTH);
    }

    public static String getRandomString(Random random) {
        return getRandomString(random, STRING_LENGTH);
    }

    public static String getRandomString(Random random, int length) {
        return RandomStringUtils.random(length, 0, 0, true, true, null, random);
    }

    public static String getRandomNumericString(Random random) {
        return getRandomNumericString(random, STRING_LENGTH);
    }

    public static String getRandomNumericString(Random random, int length) {
        return RandomStringUtils.random(length, 0, 0, false, true, null, random);
    }

    public static DateTime getRandomDate(Random random, DateTime start, DateTime end) {
        return start.plus(getRandomLimitedUInt32(random, end.getMillis() - start.getMillis()).intValue());
    }

}
