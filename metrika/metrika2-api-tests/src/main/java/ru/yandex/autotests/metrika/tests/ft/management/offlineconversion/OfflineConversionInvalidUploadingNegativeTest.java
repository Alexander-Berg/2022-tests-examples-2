package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import java.util.Arrays;
import java.util.stream.Collectors;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseContent;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.USER_ID;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OFFLINE_CONVERSION)
@Title("Невалидная загрузка офлайн конверсий")
public class OfflineConversionInvalidUploadingNegativeTest {

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
        user.onManagementSteps().onOfflineConversionSteps().uploadNonMultipartAndExpectError(
                OfflineConversionType.BASIC,
                counterId,
                ManagementError.INVALID_MULTIPART_REQUEST,
                new OfflineConversionParameters().withClientIdType(USER_ID).withIgnoreVisitJoinThreshold(1)
        );
    }

    @Test
    public void checkWrongRequestPart() {
        user.onManagementSteps().onOfflineConversionSteps().uploadWrongPartAndExpectError(
                OfflineConversionType.BASIC,
                counterId,
                ManagementError.MISSING_REQUEST_PART,
                new OfflineConversionParameters().withClientIdType(USER_ID).withIgnoreVisitJoinThreshold(1)
        );
    }

    @Test
    public void checkInvalidClientIdType() {
        user.onManagementSteps().onOfflineConversionSteps().uploadAndExpectError(
                OfflineConversionType.BASIC,
                counterId,
                Arrays.stream(createBaseContent(OfflineConversionType.BASIC, USER_ID))
                        .map(Object::toString)
                        .collect(Collectors.joining(System.lineSeparator())),
                ManagementError.WRONG_PARAMETER_VALUE,
                new OfflineConversionParameters().withClientIdType("__invalid_client_id_type__").withIgnoreVisitJoinThreshold(1)
        );
    }

    @Test
    public void checkCommentWithNotAllowedSymbols() {
        user.onManagementSteps().onOfflineConversionSteps().uploadAndExpectError(
                OfflineConversionType.BASIC,
                counterId,
                Arrays.stream(createBaseContent(OfflineConversionType.BASIC, USER_ID))
                        .map(Object::toString)
                        .collect(Collectors.joining(System.lineSeparator())),
                ManagementError.NOT_ALLOWED_SYMBOLS_IN_COMMENT,
                new OfflineConversionParameters().withClientIdType(USER_ID).withIgnoreVisitJoinThreshold(1).withComment("\uD83D\uDCC5")
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
