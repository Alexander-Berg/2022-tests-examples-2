package ru.yandex.metrika.mobmet.profiles;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils;

import static java.lang.String.format;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils.decimalCeil;

/**
 * Тесты на метод {@link ProfilesCustomNumberIntervalAttributeUtils#decimalCeil(double, int)}
 */
@RunWith(Parameterized.class)
public class DecimalCeilTest {

    @Parameter
    public double number;

    @Parameter(1)
    public int digits;

    @Parameter(2)
    public double expectedRoundedNumber;

    @Parameters(name = "decimalCeil({0}, {1}) == {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                // Digits: 2
                .add(params(0.00231293, 2, 0.0024))
                .add(params(0.231293, 2, 0.24))
                .add(params(2.31293, 2, 2.4))
                .add(params(23.1293, 2, 24.0))
                .add(params(231293, 2, 240000))
                // Digits: 2, no round
                .add(params(0.002, 2, 0.002))
                .add(params(0.2, 2, 0.2))
                .add(params(2, 2, 2))
                .add(params(2.2, 2, 2.2))
                .add(params(20, 2, 20))

                // Digits: 1
                .add(params(0.022, 1, 0.03))
                .add(params(0.22, 1, 0.3))
                .add(params(2.2, 1, 3.0))
                .add(params(22.0, 1, 30.0))
                // Digits:1, no round
                .add(params(0.2, 1, 0.2))
                .add(params(2.0, 1, 2.0))
                .build();
    }

    @Test
    public void checkRoundedNumberIsExpected() {
        double actualRoundedNumber = decimalCeil(number, digits);

        // Сравниваем через == потому что нам так же важно отсутствие ошибки вычислений.
        // Не используем здесь assertEquals без delta, потому что метод Deprecated
        assertTrue(format("Rounded number is unexpected. Expected %s, Actual: %s", expectedRoundedNumber, actualRoundedNumber),
                expectedRoundedNumber == actualRoundedNumber);
    }

    private static Object[] params(double number, int digits, double expectedRoundedNumber) {
        return new Object[]{number, digits, expectedRoundedNumber};
    }
}
