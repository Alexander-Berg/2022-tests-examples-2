package ru.yandex.metrika.mobmet.profiles;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeParams;
import ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils;
import ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils.IntervalBorder;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils.determineIntervalBorder;

/**
 * Тесты на метод {@link ProfilesCustomNumberIntervalAttributeUtils#determineIntervalBorder(IntervalBorder, double, ProfilesCustomNumberIntervalAttributeParams)}
 */
@RunWith(Parameterized.class)
public class ProfilesCustomNumberIntervalAttributeTypeConverterTest {

    private static final String PLUS_INF = String.valueOf(Double.POSITIVE_INFINITY);
    private static final String MINUS_INF = String.valueOf(Double.NEGATIVE_INFINITY);
    private static final String NAN = String.valueOf(Double.NaN);

    @Parameter
    public double id;

    @Parameter(1)
    public boolean integerIntervals;

    @Parameter(2)
    public double intervalsLength;

    @Parameter(3)
    public String expectedFrom;

    @Parameter(4)
    public String expectedTo;

    @Parameters(name = "Integer: {1}. Len: {2}. Convert {0} --> {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(params(0, true, 10, "0.0", "9.0"))
                .add(params(4, true, 10, "40.0", "49.0"))
                .add(params(-1, true, 10, "-10.0", "-1.0"))

                .add(params(0, false, 10, "0.0", "10.0"))
                .add(params(4, false, 10, "40.0", "50.0"))
                .add(params(-1, false, 10, "-10.0", "0.0"))

                .add(params(0, false, 2.5, "0.0", "2.5"))
                .add(params(4, false, 2.5, "10.0", "12.5"))
                .add(params(-1, false, 2.5, "-2.5", "0.0"))

                .add(params(0, false, 0.001, "0.0", "0.001"))
                .add(params(4, false, 0.001, "0.004", "0.005"))
                .add(params(-1, false, 0.001, "-0.001", "0.0"))

                .add(params(Double.POSITIVE_INFINITY, false, 0.001, PLUS_INF, PLUS_INF))
                .add(params(Double.NEGATIVE_INFINITY, false, 0.001, MINUS_INF, MINUS_INF))
                .add(params(Double.NaN, false, 0.001, NAN, NAN))
                .build();
    }

    @Test
    public void checkBordersAreExpected() {
        String from = determineIntervalBorder(IntervalBorder.FROM,
                id, new ProfilesCustomNumberIntervalAttributeParams(integerIntervals, intervalsLength));
        String to = determineIntervalBorder(IntervalBorder.TO,
                id, new ProfilesCustomNumberIntervalAttributeParams(integerIntervals, intervalsLength));

        assertEquals(expectedFrom + " - " + expectedTo, from + " - " + to);
    }

    private static Object[] params(double id, boolean integerIntervals, double intervalsLength, String expectedFrom, String expectedTo) {
        return new Object[]{id, integerIntervals, intervalsLength, expectedFrom, expectedTo};
    }
}
