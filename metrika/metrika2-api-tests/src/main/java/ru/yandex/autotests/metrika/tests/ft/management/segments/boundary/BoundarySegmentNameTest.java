package ru.yandex.autotests.metrika.tests.ft.management.segments.boundary;

import org.apache.commons.lang3.StringUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getSegmentName;

/**
 * Created by konkov on 19.11.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Граничные тесты на имя сегмента")
public class BoundarySegmentNameTest {
    private static final int MAX_NAME_LENGTH = 255;
    private static UserSteps user;

    private Segment segment;
    private Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
    }

    @Before
    public void setup() {
        segment = getDefaultSegment();

        CounterFull counter = new CounterFull()
                .withName(ManagementTestData.getCounterName())
                .withSite(ManagementTestData.getCounterSite());

        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter).getId();
    }

    @Test
    public void segmentsBoundaryEmptyNameTest() {
        segment.setName(StringUtils.EMPTY);

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ManagementError.INVALID_LENGTH,
                counterId,
                segment);
    }

    @Test
    public void segmentsBoundaryDuplicateNameTest() {
        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(
                counterId,
                segment);

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ManagementError.SEGMENT_ALREADY_EXISTS,
                counterId,
                segment);
    }

    @Test
    @Issue("METR-14926")
    public void segmentsBoundaryNoDuplicateNameAfterDeleteTest() {
        Long segmentId = user.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, segment).getSegmentId();

        user.onManagementSteps().onSegmentsSteps().deleteSegmentAndExpectSuccess(counterId, segmentId);

        user.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, segment);
    }

    @Test
    public void segmentsBoundaryLongestNameTest() {
        segment.setName(getSegmentName(MAX_NAME_LENGTH));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(
                counterId,
                segment);

    }

    @Test
    public void segmentsBoundaryMoreThanLongestNameTest() {
        segment.setName(getSegmentName(MAX_NAME_LENGTH + 1));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ManagementError.INVALID_LENGTH,
                counterId,
                segment);

    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
