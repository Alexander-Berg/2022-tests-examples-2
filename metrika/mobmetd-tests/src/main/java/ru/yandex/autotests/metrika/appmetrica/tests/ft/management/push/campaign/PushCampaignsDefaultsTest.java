package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.campaignWithSingleMessage;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.MUTABLE_CONTENT;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper.wrap;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.I_OS;

@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.ADD
})
@Title("Defaults пуш кампании")
public class PushCampaignsDefaultsTest {
    private static final User OWNER = Users.SUPER_LIMITED;

    private static final UserSteps user = UserSteps.onTesting(OWNER);

    private PushCampaignAdapter addedCampaign;

    @Before
    public void setup() {
        PushCampaignWrapper campaignToAdd = wrap(campaignWithSingleMessage(I_OS));
        addedCampaign = user.onPushCampaignSteps().addCampaign(campaignToAdd);
    }

    @Test
    public void checkActualCampaign() {
        assertThat("апи вернул верный default для ios mutable_content",
                addedCampaign.getHypotheses().get(0)
                        .getMessages().get(I_OS)
                        .getContents().get("ru")
                        .getContent().get(MUTABLE_CONTENT.getFieldName()),
                equalTo(1.0));
    }

    @After
    public void teardown() {
        user.onPushCampaignSteps().deleteCampaignIgnoringStatus(addedCampaign.getId());
    }
}
