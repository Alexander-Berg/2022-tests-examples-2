package ru.yandex.autotests.audience.management.tests.segments.pixel;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.pixel.PixelSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 10.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.PIXEL
})
@Title("Пиксель: изменение сегмента с типом «pixel» (негативные тесты)")
@RunWith(Parameterized.class)
public class EditPixelSegmentNegativeTest {
     private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);

     private static PixelSegment pixelSegment;
     private static PixelSegment segmentToChange;

     @Parameter
     public String description;

     @Parameter(1)
     public String newName;

     @Parameter(2)
     public IExpectedError error;

     @Parameterized.Parameters(name = "{0}: {2}")
     public static Collection<Object[]> createParameters() {
         return ImmutableList.of(
                 getEmptySegmentNameParams(),
                 getTooLongSegmentNameParams(),
                 getNullSegmentNameParams()
         );
     }

     @BeforeClass
     public static void init() {
         pixelSegment = user.onSegmentsSteps().createPixel(getPixelSegment());
     }

     @Before
     public void setup() {
         segmentToChange = getSegmentToChange(pixelSegment, newName);
     }

     @Test
     public void checkTryEditPixelSegment() {
         user.onSegmentsSteps().editSegmentAndExpectError(error, pixelSegment.getId(), segmentToChange);
     }

     @AfterClass
     public static void cleanUp() {
         user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(pixelSegment.getId());
     }
}
