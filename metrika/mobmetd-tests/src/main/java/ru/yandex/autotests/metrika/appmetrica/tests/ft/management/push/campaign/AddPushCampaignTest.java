package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.irt.testutils.beandiffer2.Diff;
import ru.yandex.autotests.irt.testutils.beandiffer2.differ.AbstractDiffer;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.matchers.DoubleValueDiffer;
import ru.yandex.autotests.metrika.appmetrica.parameters.PushCampaignsListParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignBriefAdapter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Objects;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper.wrap;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.ANDROID;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.I_OS;

/**
 * Создание новой пуш кампании
 * <p>
 * Created by graev on 22/09/16.
 */

@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.ADD,
        Requirements.Story.PushCampaign.LIST
})
@Title("Создание пуш кампании")
@RunWith(Parameterized.class)
public class AddPushCampaignTest {

    private static final User OWNER = Users.SUPER_LIMITED;

    private static final UserSteps user = UserSteps.onTesting(OWNER);

    private PushCampaignAdapter addedCampaign;

    private Long addedCampaignId;

    @Parameter
    public String testDescription;

    @Parameter(1)
    public PushCampaignWrapper campaignToAdd;

    @Parameter(2)
    public PushCampaignAdapter expectedCamapign;

    @Parameter(3)
    public PushCampaignBriefAdapter expectedBriefCampaign;

    public Long appId;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param("Minimal campaign", minimalCampaign()))
                .add(param("Campaign with sendRate", minimalCampaign().withSendRate(500L)))
                .add(param("Campaign for large application", campaignForLargeApplication()))
                .add(param("Silent campaign", silentCampaign()))
                .add(param("Delayed campaign with app time zone", delayedCampaignWithAppTimeZone()))
                .add(param("Delayed campaign with devices time zone", delayedCampaignWithDeivcesTimeZone()))
                .add(param("Campaign with full android message", updateMessagesContent(
                        campaignWithSingleMessage(ANDROID),
                        fullAndroidContent()
                )))
                .add(param("Campaign with full iOS message", updateMessagesContent(
                        campaignWithSingleMessage(I_OS),
                        fullIOsContent()
                )))
                .build();
    }

    @Before
    public void setup() {
        appId = campaignToAdd.getCampaign().getAppId();
        addedCampaign = user.onPushCampaignSteps().addCampaign(campaignToAdd);
        addedCampaignId = addedCampaign.getId();
    }

    @Test
    public void checkCampaignInfo() {
        assertThat("добавленная кампания эквивалентна ожидаемой", addedCampaign,
                pushCampaignEquivalentTo(expectedCamapign));
    }

    @Test
    public void checkActualCampaign() {
        PushCampaignAdapter actualCampaign = user.onPushCampaignSteps().getCampaign(addedCampaign.getId());

        assertThat("актуальная кампания эквивалентна ожидаемой", actualCampaign,
                pushCampaignEquivalentTo(expectedCamapign));
    }

    @Test
    public void checkCampaignInList() {
        // Запрашиваем список пуш-кампаний для указанного target uid-а, потому что SUPER_LIMITED так может.
        // Иначе нужно было бы выдать грант на приложение, а для приложений yastorepublisher это делается только через IDM.
        final long appOwnerUid = user.onApplicationSteps().getApplication(appId).getUid();
        final List<PushCampaignBriefAdapter> campaigns = user.onPushCampaignSteps()
                .getCampaignList(new PushCampaignsListParameters().withAppId(appId).withUid(appOwnerUid)).getCampaigns();
        assertThat("список кампаний содержит кампанию, эквивалентную ожидаемой", campaigns,
                hasItem(equivalentTo(expectedBriefCampaign)));
    }

    @After
    public void teardown() {
        user.onPushCampaignSteps().deleteCampaignIgnoringStatus(addedCampaignId);
    }

    private static Object[] param(String testDescription, PushCampaignAdapter campaign) {
        return toArray(testDescription, wrap(campaign), campaign, briefInfo(campaign));
    }

    public static Matcher<PushCampaignAdapter> pushCampaignEquivalentTo(PushCampaignAdapter pushCampaign) {
        ApiARGBColorDiffer argbColorDiffer = new ApiARGBColorDiffer();
        return equivalentTo(
                pushCampaign,
                ImmutableMap.of(Double.class, new DoubleValueDiffer()),
                ImmutableMap.of(
                        "hypotheses/0/messages/android/contents/ru/content/led_color", argbColorDiffer,
                        "hypotheses/0/messages/android/contents/ru/content/icon_background", argbColorDiffer
                )
        );
    }

    private static class ApiARGBColorDiffer extends AbstractDiffer {
        @Override
        public List<Diff> compare(Object actual, Object expected) {
            if (actual == null && expected == null) {
                return emptyList();
            }
            if (actual == null || expected == null) {
                return singletonList(Diff.changed(getField(), Objects.toString(actual), Objects.toString(expected)));
            }

            List<Diff> result = new ArrayList<>();
            String expectedColor = toApiARGBColor((String) expected);
            String actualColor = toApiARGBColor((String) actual);

            Matcher<String> matcher = equalTo(expectedColor);
            if (!matcher.matches(actualColor)) {
                result.add(Diff.changed(getField(), actual, matcher.toString()));
            }
            return result;
        }

        private String toApiARGBColor(String argbColor) {
            if (argbColor.length() == 7) {
                argbColor = "#ff" + argbColor.substring(1);
            }
            return argbColor.toLowerCase();
        }
    }
}
