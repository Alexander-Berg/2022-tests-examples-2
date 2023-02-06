package ru.yandex.autotests.audience.management.tests.pixel;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.pixel.Pixel;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.errors.ManagementError.PIXEL_HAS_DEPENDENT_SEGMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.getPixelName;
import static ru.yandex.autotests.audience.management.tests.TestData.getPixelSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 28.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.PIXELS})
@Title("Pixel: удаление пикселя (негативные тесты)")
public class DeletePixelNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    private static Long pixelId;
    private static Long pixelSegmentId;

    @BeforeClass
    public static void init() {
        pixelId = user.onPixelsSteps().createPixel(getPixelName()).getId();
        pixelSegmentId = user.onSegmentsSteps().createPixel(getPixelSegment(pixelId)).getId();
    }

    @Test
    public void checkTryDeletePixel() {
        user.onPixelsSteps().deletePixelAndExpectError(PIXEL_HAS_DEPENDENT_SEGMENTS, pixelId);
    }

    @Test
    public void checkPixelIsStillInList() {
        List<Pixel> pixels = user.onPixelsSteps().getPixels();

        assertThat("пиксель присутствует в списке", pixels.stream().map(Pixel::getId).collect(toList()),
                hasItem(pixelId));
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(pixelSegmentId);
        user.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId);
    }
}
