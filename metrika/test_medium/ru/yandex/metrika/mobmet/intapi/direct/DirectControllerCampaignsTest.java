package ru.yandex.metrika.mobmet.intapi.direct;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.mobmet.bundleid.AppleAppIdDao;
import ru.yandex.metrika.mobmet.bundleid.AppleAppIdMatching;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestData;
import ru.yandex.metrika.mobmet.intapi.common.TestTvmServices;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectBundleId;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectPlatform;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectUniversalCampaignRequest;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;
import ru.yandex.metrika.mobmet.model.redirect.CampaignSource;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class DirectControllerCampaignsTest extends AbstractMobmetIntapiTest {

    private static final ObjectMapper OBJECT_MAPPER = ObjectMappersFactory.getDefaultMapper();

    @Autowired
    private ApplicationsManageService applicationsManageService;
    @Autowired
    private AuthUtils authUtils;
    @Autowired
    private AppleAppIdDao appleAppIdDao;

    @Test
    public void createUniversalAppCampaign() throws Exception {
        String campaignName = "My campaign name";
        String androidBundleId = "ru.app.myapp";
        String iosBundleId = "app.tasti.pushkinpirogi";
        int iosAppStoreId = 42;

        DirectUniversalCampaignRequest request = new DirectUniversalCampaignRequest(
                Map.of(
                        DirectPlatform.ANDROID, new DirectBundleId(androidBundleId),
                        DirectPlatform.IOS, new DirectBundleId(iosBundleId)),
                campaignName);

        appleAppIdDao.save(List.of(new AppleAppIdMatching(iosAppStoreId, iosBundleId)));

        var user = authUtils.getUserByUid(TestData.randomUid());
        var app = applicationsManageService.createApplication(TestData.defaultApp(), user, user);

        String requestContent = OBJECT_MAPPER.writeValueAsString(request);

        mockMvc.perform(post("/direct/v1/universal_campaign")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders())
                .content(requestContent)
                .param("uid", Objects.toString(user.getUid()))
                .param("app_id", Objects.toString(app.getId())))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk());
    }

    @Test
    public void loadUniversalAppCampaigns() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var app = applicationsManageService.createApplication(TestData.defaultApp(), user, user);

        mockMvc.perform(get("/direct/v1/campaigns")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders())
                .param("uid", Objects.toString(user.getUid()))
                .param("app_id", Objects.toString(app.getId()))
                .param("source", CampaignSource.direct_uac.name())
                .param("remarketing", "false"))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk());
    }
}
