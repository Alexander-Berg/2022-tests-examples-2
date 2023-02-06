package ru.yandex.metrika.mobmet.intapi.takeout;

import org.assertj.core.api.Condition;
import org.assertj.core.data.Index;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestData;
import ru.yandex.metrika.mobmet.intapi.takeout.service.TakeoutService;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;

import static org.assertj.core.api.Assertions.assertThat;

public class TakeoutServiceTest extends AbstractMobmetIntapiTest {

    @Autowired
    private ApplicationsManageService applicationsManageService;
    @Autowired
    private AuthUtils authUtils;
    @Autowired
    private TakeoutService takeoutService;

    @Test
    public void takeoutApplication() {
        MetrikaUserDetails user = authUtils.getUserByUid(TestData.randomUid());
        var addedApp = applicationsManageService.createApplication(TestData.defaultApp(), user, user);

        TakeoutResponse response = takeoutService.takeout(user.getUid());

        TakeoutOkResponse okResponse = TakeoutTestUtils.readOkTakeoutResponse(response);
        assertThat(okResponse.getApplications())
                .hasSize(1)
                .has(new Condition<>(a -> a.getApplicationId() == addedApp.getId(), "appId check"), Index.atIndex(0));
    }


}
