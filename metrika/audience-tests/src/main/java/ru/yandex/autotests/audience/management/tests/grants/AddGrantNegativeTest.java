package ru.yandex.autotests.audience.management.tests.grants;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Доступ: выдача доступа на сегмент (негативные тесты)")
@RunWith(Parameterized.class)
public class AddGrantNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    private static Long segmentId;
    private static Long dmpSegmentId;

    @Parameter()
    public String description;

    @Parameter(1)
    public Grant grant;

    @Parameter(2)
    public Long segmentIdParam;

    @Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {3}")
    public static Collection<Object[]> createParameters() {
        segmentId = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST)).getId();
        dmpSegmentId = user.onSegmentsSteps().createDmp(SegmentRequestDmpWrapper.wrap(getDmpSegment())).getId();
        user.onGrantsSteps().createGrant(segmentId, getGrant(USER_FOR_LOOKALIKE));

        return ImmutableList.of(
                createGrantNegativeParam("несуществующий сегмент", RandomUtils.getString(15), segmentId,
                        USER_NOT_FOUND),
                createGrantNegativeParam("доступ на «dmp» сегмент", USER_GRANTEE.toString(), dmpSegmentId,
                    NO_GRANT_FOR_DMP),
                createGrantNegativeParam("пустой userLogin", StringUtils.EMPTY, segmentId, NOT_EMPTY),
                createGrantNegativeParam("в отправляемом json отсуствует поле userLogin", null,
                        segmentId, NOT_EMPTY),
                createGrantNegativeParam("повторная выдача доступа", USER_FOR_LOOKALIKE.toString(), segmentId,
                        GRANT_HAS_ALREADY_CREATED)
        );
    }

    @Test
    public void checkTryAddGrant() {
        user.onGrantsSteps().createGrantAndExpectError(error, segmentIdParam, grant);
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(dmpSegmentId);
    }
}
