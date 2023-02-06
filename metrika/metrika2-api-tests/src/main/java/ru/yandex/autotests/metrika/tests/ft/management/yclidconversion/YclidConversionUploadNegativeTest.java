package ru.yandex.autotests.metrika.tests.ft.management.yclidconversion;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.conversion.CommonConversionUploadingTestData.createContentWithMalformedHeader;
import static ru.yandex.autotests.metrika.tests.ft.management.conversion.CommonConversionUploadingTestData.createEmptyContent;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithMalformedData;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithoutData;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.YCLID_CONVERSION)
@Title("Загрузка yclid конверсий, негативные")
@RunWith(Parameterized.class)
public class YclidConversionUploadNegativeTest {

    private static UserSteps user;
    private static Long counterId;

    @Parameterized.Parameter
    public String name;

    @Parameterized.Parameter(1)
    public String content;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return asList(
                createEmptyContent(),
                createContentWithMalformedHeader(),
                createContentWithoutData(),
                createContentWithMalformedData()
        );
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void checkUpload() {
        user.onManagementSteps().onYclidConversionSteps().uploadAndExpectError(
                counterId,
                content,
                ManagementError.INVALID_UPLOADING,
                new OfflineConversionParameters().withIgnoreVisitJoinThreshold(1)
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
