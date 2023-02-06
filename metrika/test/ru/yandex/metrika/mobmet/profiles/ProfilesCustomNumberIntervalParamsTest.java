package ru.yandex.metrika.mobmet.profiles;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeParams;
import ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils.EPS;
import static ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils.determineIntervalAttributeParams;
import static ru.yandex.metrika.segments.apps.misc.profile.ProfilesCustomNumberIntervalAttributeUtils.isInteger;

/**
 * Тесты на метод {@link ProfilesCustomNumberIntervalAttributeUtils#determineIntervalAttributeParams(Double, boolean, double, double)}
 */
@RunWith(Parameterized.class)
public class ProfilesCustomNumberIntervalParamsTest {

    @Parameter
    public Double intervalsLength;

    @Parameter(1)
    public boolean hasFloatValues;

    @Parameter(2)
    public double minValue;

    @Parameter(3)
    public double maxValue;

    @Parameter(4)
    public boolean expectedParamsPresent;

    @Parameter(5)
    public Class<? extends Exception> expectedExceptionType;

    @Rule
    public ExpectedException expectedException = ExpectedException.none();

    private ProfilesCustomNumberIntervalAttributeParams actualParams;

    @Parameters(name = "Input len: {0}. HasFloatValues: {1}. Values: [{2} - {3}]")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                // Целые
                .add(expectDefinedParamsFor(4.0, false, 0.0, 10.0))
                .add(expectDefinedParamsFor(null, false, 0.0, 10.0))

                // Дробные
                .add(expectDefinedParamsFor(4.0, true, 0.0, 10.0))
                .add(expectDefinedParamsFor(null, true, 0.0, 10.0))

                // Маленькая разница (целые)
                .add(expectUndefinedParamsFor(4.0, false, 10.0, 10.0))
                .add(expectUndefinedParamsFor(0.0, false, 10.0, 10.0))
                .add(expectUndefinedParamsFor(null, false, 10.0, 10.0))

                // Маленькая разница (дробные)
                .add(expectUndefinedParamsFor(4.0, true, 10.0, 10.0))
                .add(expectUndefinedParamsFor(4.0, true, 10.0, 10.0 + EPS * 0.1))
                .add(expectUndefinedParamsFor(0.0, true, 10.0, 10.0))
                .add(expectUndefinedParamsFor(0.0, true, 10.0, 10.0 + EPS * 0.1))
                .add(expectUndefinedParamsFor(null, true, 10.0, 10.0))
                .add(expectUndefinedParamsFor(null, true, 10.0, 10.0 + EPS * 0.1))

                // Маленькая длина
                .add(expectUndefinedParamsFor(0.0, false, 0.0, 10.0))
                .add(expectUndefinedParamsFor(0.0, true, 0.0, 10.0))
                .add(expectUndefinedParamsFor(EPS * 0.1, true, 0.0, 10.0))
                .add(expectDefinedParamsFor(EPS, true, 0.0, 10.0))

                /// Ошибки аргументов

                // len < 0
                .add(expectValidationExpectionFor(-1.0, true, 10.0, 10.0))
                .add(expectValidationExpectionFor(-1.0, false, 10.0, 10.0))

                // min > max
                .add(expectValidationExpectionFor(4.0, true, 10.0, 0))
                .add(expectValidationExpectionFor(4.0, false, 10.0, 0))

                // Проверяем реакцию на противоречие предварительных метрик: hasFloatValues = false с дробными min и max
                .add(expectValidationExpectionFor(4.0, false, 0.0, 10.5))
                .add(expectValidationExpectionFor(4.0, false, 0.5, 10.0))

                .build();
    }

    @Before
    public void setup() {
        if (expectedExceptionType != null) {
            expectedException.expect(expectedExceptionType);
        }
        actualParams = determineIntervalAttributeParams(intervalsLength, hasFloatValues, minValue, maxValue).orElse(null);
    }

    @Test
    public void checkExpectedParamsPresent() {
        if (expectedParamsPresent) {
            assertNotNull(actualParams);
        }
    }

    @Test
    public void checkDefinedLengthIsNotSmall() {
        if (actualParams != null) {
            assertTrue(actualParams.getIntervalsLength() >= EPS);
        }
    }

    @Test
    public void checkDefinedIntegerLength() {
        if (actualParams != null && actualParams.isIntegerIntervals()) {
            assertTrue(isInteger(actualParams.getIntervalsLength()));
        }
    }

    private static Object[] expectDefinedParamsFor(Double intervalsLength, boolean hasFloatValues, double minValue, double maxValue) {
        return new Object[]{intervalsLength, hasFloatValues, minValue, maxValue, true, null};
    }

    private static Object[] expectUndefinedParamsFor(Double intervalsLength, boolean hasFloatValues, double minValue, double maxValue) {
        return new Object[]{intervalsLength, hasFloatValues, minValue, maxValue, false, null};
    }

    private static Object[] expectValidationExpectionFor(Double intervalsLength, boolean hasFloatValues, double minValue, double maxValue) {
        return new Object[]{intervalsLength, hasFloatValues, minValue, maxValue, false, IllegalArgumentException.class};
    }
}
