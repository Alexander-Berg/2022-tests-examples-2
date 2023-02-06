package ru.yandex.autotests.audience.management.tests.segments.appmetrica;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.AppMetricaSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestAppMetrika;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.User.APPMETRICA_APLICATION_ID;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.TOO_LONG_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.management.tests.TestData.getAppMetricaSegment;

/**
 * Created by ava1on on 25.10.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.APPMETRICA
})
@Title("AppMetrica: создание сегмента из объекта AppMetrica (негативные тесты)")
@RunWith(Parameterized.class)
public class CreateAppMetricaSegmentNegativeTest {
    private static final User WITH_ACCESS = USER_FOR_LOOKALIKE;
    private static final User NO_ACCESS = SIMPLE_USER;
    private static final UserSteps user = UserSteps.withUser(WITH_ACCESS);

    @Parameter
    public String descritpion;

    @Parameter(1)
    public SegmentRequestAppMetrika segmentRequest;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameter() {
        return ImmutableList.of(
                toArray("пустой name",
                        getAppMetricaSegment(AppMetricaSegmentType.API_KEY, WITH_ACCESS).withName(StringUtils.EMPTY),
                        INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует name",
                        getAppMetricaSegment(AppMetricaSegmentType.SEGMENT_ID, WITH_ACCESS).withName(null),
                        NOT_NULL),
                toArray("слишком длинный name",
                        getAppMetricaSegment(AppMetricaSegmentType.API_KEY, WITH_ACCESS).withName(TOO_LONG_SEGMENT_NAME_LENGTH),
                        INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует metrika_segment_type",
                        getAppMetricaSegment(AppMetricaSegmentType.SEGMENT_ID, WITH_ACCESS).withAppMetricaSegmentType(null),
                        NOT_NULL),
                toArray("отсутствует metrika_segment_id",
                        getAppMetricaSegment(AppMetricaSegmentType.API_KEY, WITH_ACCESS).withAppMetricaSegmentId(null),
                        ACCESS_DENIED_FOR_API_KEY),
                toArray("не совпадают type и id",
                        getAppMetricaSegment(AppMetricaSegmentType.SEGMENT_ID, WITH_ACCESS)
                                .withAppMetricaSegmentId(WITH_ACCESS.get(APPMETRICA_APLICATION_ID)),
                        NO_OBJECT),
                toArray("нет доступа к счетчику",
                        getAppMetricaSegment(AppMetricaSegmentType.API_KEY, WITH_ACCESS)
                                .withAppMetricaSegmentId(NO_ACCESS.get(APPMETRICA_APLICATION_ID)),
                        ACCESS_DENIED_FOR_API_KEY)
        );
    }

    @Test
    public void checkTryCreateAppMetricaSegmentNegativeTest() {
        user.onSegmentsSteps().createAppMetricaAndExpectError(error, segmentRequest);
    }
}
