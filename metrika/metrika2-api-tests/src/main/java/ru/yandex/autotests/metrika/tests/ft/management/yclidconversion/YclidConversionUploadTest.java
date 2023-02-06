package ru.yandex.autotests.metrika.tests.ft.management.yclidconversion;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploading;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createBaseContent;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithAllValuesEmpty;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithChangedHeaderCase;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithEmptyLines;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithNonWordCharsInHeader;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithShuffledColumns;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithULongYclid;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createContentWithUntrimmedValues;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.YCLID_CONVERSION)
@Title("Загрузка yclid конверсий")
@RunWith(Parameterized.class)
public class YclidConversionUploadTest {

    private static UserSteps user;
    private static Long counterId;

    @Parameterized.Parameter
    public String name;

    @Parameterized.Parameter(1)
    public String content;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return asList(
                createBaseContent(),
                createContentWithChangedHeaderCase(),
                createContentWithNonWordCharsInHeader(),
                createContentWithShuffledColumns(),
                createContentWithEmptyLines(),
                createContentWithUntrimmedValues(),
                createContentWithAllValuesEmpty(),
                createContentWithULongYclid()
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
        OfflineConversionUploading uploading = user.onManagementSteps().onYclidConversionSteps()
                .upload(counterId, content, new OfflineConversionParameters()
                        .withIgnoreVisitJoinThreshold(1)
                );

        assertThat(
                "загрузка корректно создалась",
                uploading,
                beanEquivalent(new OfflineConversionUploading()
                        .withLineQuantity(1L)
                        .withStatus(OfflineConversionUploadingStatus.UPLOADED)
                ).withVariation(new DefaultMatchVariation()
                        .forFields("id", "createTime")
                        .useMatcher(notNullValue())
                )
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
