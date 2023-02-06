package ru.yandex.autotests.metrika.tests.ft.management.yclidconversion;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.YCLID_CONVERSION)
@Title("Невалидная загрузка yclid конверсий")
public class YclidConversionInvalidUploadingNegativeTest {

    private static UserSteps user = new UserSteps();
    private static Long counterId;

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void checkInvalidMultipartRequest() {
        user.onManagementSteps().onYclidConversionSteps().uploadNonMultipartAndExpectError(
                counterId,
                ManagementError.INVALID_MULTIPART_REQUEST
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
