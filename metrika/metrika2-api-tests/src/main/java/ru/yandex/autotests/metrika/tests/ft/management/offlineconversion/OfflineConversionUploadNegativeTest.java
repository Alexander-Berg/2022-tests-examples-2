package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import java.util.Collection;
import java.util.function.Function;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.BASIC;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.conversion.CommonConversionUploadingTestData.createContentWithMalformedHeader;
import static ru.yandex.autotests.metrika.tests.ft.management.conversion.CommonConversionUploadingTestData.createEmptyContent;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithMalformedData;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithoutData;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithoutNonOptionalColumns;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.CLIENT_ID;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.USER_ID;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.YCLID;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OFFLINE_CONVERSION)
@Title("Загрузка офлайн конверсий, негативные")
@RunWith(Parameterized.class)
public class OfflineConversionUploadNegativeTest {

    private static UserSteps user;
    private static Long counterId;

    @Parameterized.Parameter
    public OfflineConversionUploadingClientIdType clientIdType;

    @Parameterized.Parameter(1)
    public String name;

    @Parameterized.Parameter(2)
    public String content;

    @Parameterized.Parameters(name = "{1}, тип идентификатора клиента {0}")
    public static Collection<Object[]> getParameters() {
        return MultiplicationBuilder.<OfflineConversionUploadingClientIdType, OfflineConversionUploadingClientIdType, Object[]>builder(
                ImmutableList.copyOf(OfflineConversionUploadingClientIdType.values()), () -> new Object[] {})

                // all negative cases for USER_ID
                .apply(USER_ID::equals, (clientIdType, objects) -> ImmutableList.<Object[]>builder()
                        .add(createEmptyContent())
                        .add(createContentWithMalformedHeader())
                        .add(createContentWithoutData(BASIC, clientIdType))
                        .add(createContentWithMalformedData(BASIC, clientIdType))
                        .addAll(createContentWithoutNonOptionalColumns(BASIC, clientIdType))
                        .build()
                        .stream()
                        .map(objs -> ImmutablePair.of(clientIdType, objs)))

                // specific negative cases for CLIENT_ID
                .apply(CLIENT_ID::equals, (clientIdType, objects) -> ImmutableList.<Object[]>builder()
                        .addAll(createContentWithoutNonOptionalColumns(BASIC, clientIdType, of(BASIC.getClientIdColumn())))
                        .build()
                        .stream()
                        .map(objs -> ImmutablePair.of(clientIdType, objs)))

                // specific negative cases for YCLID
                .apply(YCLID::equals, (clientIdType, objects) -> ImmutableList.<Object[]>builder()
                        .addAll(createContentWithoutNonOptionalColumns(BASIC, clientIdType, of(BASIC.getYclidColumn())))
                        .build()
                        .stream()
                        .map(objs -> ImmutablePair.of(clientIdType, objs)))
                .build(Function.identity(), Function.identity());
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
        user.onManagementSteps().onOfflineConversionSteps()
                .uploadAndExpectError(BASIC, counterId, content, ManagementError.INVALID_UPLOADING,
                        new OfflineConversionParameters().withClientIdType(clientIdType).withIgnoreVisitJoinThreshold(1));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
