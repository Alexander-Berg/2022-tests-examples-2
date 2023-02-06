package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.RandomStringUtils;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.PushValidationMessage;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.ErrorLocationAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.LaunchStatusAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.ValidationErrorAdapter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.stream.Stream;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Collections.singletonMap;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.appmetrica.errors.PushValidationMessage.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.PushCampaignValidationTest.ExpectedResult.EXPECT_ERROR;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.PushCampaignValidationTest.ExpectedResult.EXPECT_OK;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper.wrap;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.*;

/**
 * Проверяем, что валидация пуш кампаний работает нормально
 */
@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.ADD,
        Requirements.Story.PushCampaign.LAUNCH
})
@Title("Валидация пуш кампании")
@RunWith(Parameterized.class)
public final class PushCampaignValidationTest {

    private static final User OWNER = Users.SUPER_LIMITED;

    private static final UserSteps user = UserSteps.onTesting(OWNER);

    // Сейчас максимальный допустимый размер payload для Android и iOS равен 4096 байтам. Но необходимо еще оставить
    // резерв на издержки протокола, названия полей, ряд служебных полей
    private static final int PAYLOAD_SIZE_LIMIT = 4096;
    private static final int PAYLOAD_PROTOCOL_OVERHEAD = 207;

    @Parameterized.Parameter
    public String testDescription;

    @Parameterized.Parameter(1)
    public PushCampaignWrapper campaignToAdd;

    @Parameterized.Parameter(2)
    public PushValidationMessage errorMessage;

    @Parameterized.Parameter(3)
    public Field field;

    @Parameterized.Parameter(4)
    public ExpectedResult expectedResult;

    private Long appId;

    private Long addedCampaignId;

    private Matcher<LaunchStatusAdapter> checkStatusMatcher;

    @Parameterized.Parameters(name = "{0}; {2}; expectError: {4}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                // Check silent platform validation
                .add(param("Silent android campaign",
                        silentCampaignWithSingleMessage(ANDROID), UNSUPPORTED_SILENT_PLATFORM, EXPECT_OK))
                .add(param("Silent iOS campaign",
                        silentCampaignWithSingleMessage(I_OS), UNSUPPORTED_SILENT_PLATFORM, EXPECT_OK))
                .add(param("Silent Windows campaign",
                        silentCampaignWithSingleMessage(WINDOWS_PHONE), UNSUPPORTED_SILENT_PLATFORM, EXPECT_ERROR))

                // Check empty fields validation in silent and ordinary campaigns
                // Text
                .addAll(Stream.of(ANDROID, I_OS, WINDOWS_PHONE)
                        .map(platform -> param(
                                "Empty message, platform: " + platform,
                                campaignWithSingleMessage(platform),
                                REQUIRED_FIELD_IS_EMPTY,
                                TEXT,
                                EXPECT_ERROR))
                        .collect(toList()))
                .addAll(Stream.of(ANDROID, I_OS, WINDOWS_PHONE)
                        .map(platform -> param(
                                "Not empty message, platform: " + platform,
                                updateMessagesContent(campaignWithSingleMessage(platform),
                                        singletonMap(TEXT, "Message")),
                                REQUIRED_FIELD_IS_EMPTY,
                                TEXT,
                                EXPECT_OK))
                        .collect(toList()))
                .addAll(Stream.of(ANDROID, I_OS)
                        .map(platform -> param(
                                "Empty silent message, platform: " + platform,
                                silentCampaignWithSingleMessage(platform),
                                REQUIRED_FIELD_IS_EMPTY,
                                TEXT,
                                EXPECT_OK))
                        .collect(toList()))
                // Title
                .addAll(Stream.of(ANDROID, WINDOWS_PHONE)
                        .map(platform -> param(
                                "Empty title, platform: " + platform,
                                campaignWithSingleMessage(platform),
                                REQUIRED_FIELD_IS_EMPTY,
                                TITLE,
                                EXPECT_ERROR))
                        .collect(toList()))
                .add(param(
                        "Empty iOS title",
                        campaignWithSingleMessage(I_OS),
                        REQUIRED_FIELD_IS_EMPTY,
                        TITLE,
                        EXPECT_OK))
                .addAll(Stream.of(ANDROID, I_OS, WINDOWS_PHONE)
                        .map(platform -> param(
                                "Not empty title, platform: " + platform,
                                updateMessagesContent(campaignWithSingleMessage(platform),
                                        singletonMap(TITLE, "Message")),
                                REQUIRED_FIELD_IS_EMPTY,
                                TITLE,
                                EXPECT_OK))
                        .collect(toList()))
                .add(param(
                        "Empty silent android title",
                        silentCampaignWithSingleMessage(ANDROID),
                        REQUIRED_FIELD_IS_EMPTY,
                        TITLE,
                        EXPECT_OK))

                // Check apns-collapse-id
                .add(param(
                        "Too big apns-collapse-id",
                        updateMessagesContent(campaignWithSingleMessage(I_OS),
                                singletonMap(APNS_COLLAPSE_ID, "AppMepCollapseId_12432513451345_23145353453")),
                        FIELD_LENGTH_EXCEED,
                        APNS_COLLAPSE_ID,
                        EXPECT_OK))
                .add(param(
                        "Too big apns-collapse-id",
                        updateMessagesContent(campaignWithSingleMessage(I_OS),
                                singletonMap(APNS_COLLAPSE_ID,
                                        "AppMepCollapseId_124325134513454573465987326495786_2314535345334563874563147895697134")),
                        FIELD_LENGTH_EXCEED,
                        APNS_COLLAPSE_ID,
                        EXPECT_ERROR))

                // Check android priority
                .addAll(Stream.of(-3, 3)
                        .map(priority -> param(
                                "Illegal android priority value",
                                updateMessagesContent(campaignWithSingleMessage(ANDROID),
                                        singletonMap(PRIORITY, priority)),
                                ILLEGAL_FIELD_VALUE,
                                PRIORITY,
                                EXPECT_ERROR))
                        .collect(toList()))
                .addAll(Stream.of(-2, 2)
                        .map(priority -> param(
                                "Valid android priority value",
                                updateMessagesContent(campaignWithSingleMessage(ANDROID),
                                        singletonMap(PRIORITY, priority)),
                                ILLEGAL_FIELD_VALUE,
                                PRIORITY,
                                EXPECT_OK))
                        .collect(toList()))

                // Check android image and banner
                .addAll(Stream.of(IMAGE, BANNER)
                        .map(field -> param(
                                "Invalid android " + field,
                                updateMessagesContent(campaignWithSingleMessage(ANDROID),
                                        singletonMap(field, "ftp://images.com/1.jpeg")),
                                ANDROID_IMAGE_LINK_ERROR,
                                field,
                                EXPECT_ERROR))
                        .collect(toList()))
                .addAll(CombinatorialBuilder.builder().values(IMAGE, BANNER).values("http", "https").build().stream()
                        .map(args -> {
                            Field field = (Field) args[0];
                            String protocol = (String) args[1];
                            return param(
                                    "Valid android " + field,
                                    updateMessagesContent(campaignWithSingleMessage(ANDROID),
                                            singletonMap(field, protocol + "://images.com/1.jpeg")),
                                    ANDROID_IMAGE_LINK_ERROR,
                                    field,
                                    EXPECT_OK);
                        })
                        .collect(toList()))

                // Check android channel
                .add(param(
                        "Illegal android channel value",
                        updateMessagesContent(campaignWithSingleMessage(ANDROID),
                                singletonMap(CHANNEL_ID, "  ")),
                        ILLEGAL_FIELD_VALUE,
                        CHANNEL_ID,
                        EXPECT_ERROR))
                .add(param(
                        "Valid android channel value",
                        updateMessagesContent(campaignWithSingleMessage(ANDROID),
                                singletonMap(CHANNEL_ID, "varetbауцАКУ13123 _")),
                        ILLEGAL_FIELD_VALUE,
                        CHANNEL_ID,
                        EXPECT_OK))

                // check payload size
                .addAll(Stream.of(I_OS, ANDROID)
                        .map(platform -> param(
                                "Payload size limit exceeded",
                                updateMessagesContent(
                                        campaignWithSingleMessage(platform),
                                        singletonMap(TEXT,
                                                RandomStringUtils.randomAlphanumeric(PAYLOAD_SIZE_LIMIT))),
                                PAYLOAD_LIMIT_EXCEEDED,
                                EXPECT_ERROR))
                        .collect(toList()))
                .addAll(Stream.of(I_OS, ANDROID)
                        .map(platform -> param(
                                "Payload size limit exceeded",
                                updateMessagesContent(
                                        campaignWithSingleMessage(platform),
                                        singletonMap(TEXT, RandomStringUtils.randomAlphanumeric(
                                                PAYLOAD_SIZE_LIMIT - PAYLOAD_PROTOCOL_OVERHEAD))),
                                PAYLOAD_LIMIT_EXCEEDED,
                                EXPECT_OK))
                        .collect(toList()))

                .build();
    }

    @Before
    public void setup() {
        final Application application = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();
        campaignToAdd.getCampaign().setAppId(appId);
        final PushCampaignAdapter campaign = user.onPushCampaignSteps().addCampaign(campaignToAdd);
        addedCampaignId = campaign.getId();
        final Matcher<LaunchStatusAdapter> hasMessage =
                having(on(LaunchStatusAdapter.class).getErrors(), hasItem(allOf(
                        having(on(ValidationErrorAdapter.class).getMessage(), startsWith(errorMessage.message())),
                        having(on(ValidationErrorAdapter.class).getLocation(),
                                having(on(ErrorLocationAdapter.class).getField(), equalTo(field.getFieldName())))
                )));
        checkStatusMatcher = (expectedResult == EXPECT_ERROR ? hasMessage : not(hasMessage));
    }

    @Test
    public void checkValidationError() {
        final LaunchStatusAdapter actualStatus = user.onPushCampaignSteps().launchCampaign(addedCampaignId);
        assertThat("запуск кампании (не)содержит ожидаемую ошибку валидации", actualStatus, checkStatusMatcher);
    }

    @After
    public void tearDown() {
        user.onPushCampaignSteps().deleteCampaignIgnoringStatus(addedCampaignId);
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(String testDescription, PushCampaignAdapter campaign,
                                  PushValidationMessage error, ExpectedResult expectError) {
        return param(testDescription, campaign, error, IGNORED, expectError);
    }

    private static Object[] param(String testDescription, PushCampaignAdapter campaign,
                                  PushValidationMessage error, Field field, ExpectedResult expectError) {
        return toArray(testDescription, wrap(campaign), error, field, expectError);
    }

    public enum ExpectedResult {
        EXPECT_OK,
        EXPECT_ERROR;
    }
}
