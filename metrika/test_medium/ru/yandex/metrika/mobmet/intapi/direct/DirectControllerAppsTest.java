package ru.yandex.metrika.mobmet.intapi.direct;

import java.util.List;
import java.util.Objects;

import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultMatcher;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.mobmet.bundleid.BundleId;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestData;
import ru.yandex.metrika.mobmet.intapi.common.TestTvmServices;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectApp;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectAppsRequest;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectPlatform;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectPlatformBundleId;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;
import ru.yandex.metrika.mobmet.scheduler.tasks.bundleid.dao.BundleIdCachingDao;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.mobmet.intapi.common.TestData.defaultApp;
import static ru.yandex.metrika.segments.apps.type.OperatingSystem.ANDROID;
import static ru.yandex.metrika.util.json.ObjectMappersFactory.getDefaultMapper;

public class DirectControllerAppsTest extends AbstractMobmetIntapiTest {

    @Autowired
    private AuthUtils authUtils;
    @Autowired
    private ApplicationsManageService appManageService;
    @Autowired
    private BundleIdCachingDao bundleIdCachingDao;

    @Test
    public void missingParam() throws Exception {
        getDirectApps(new DirectAppsRequest(), status().isBadRequest());
    }

    @Test
    public void invalidParam() throws Exception {
        var request = new DirectAppsRequest().withUid(0L);
        getDirectApps(request, status().isBadRequest());
    }

    @Test
    public void missingPlatform() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withBundleId("any string");
        getDirectApps(request, status().isBadRequest());
    }

    @Test
    public void missingBundleId() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withPlatform(DirectPlatform.ANDROID);
        getDirectApps(request, status().isBadRequest());
    }

    @Test
    public void userWithoutApps() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var request = new DirectAppsRequest().withUid(user.getUid());
        var actual = getDirectApps(request, status().isOk());
        assertThat(actual).isEmpty();
    }

    @Test
    public void bundleIdSearch() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var app = appManageService.createApplication(defaultApp(), user, user);
        var app2 = appManageService.createApplication(defaultApp(), user, user);

        var appBundleId = "app_bundle_id";
        var app2BundleId = "app_bundle_id2";
        bundleIdCachingDao.addToCacheWithoutRowsCount(List.of(
                new BundleId(app.getId(), ANDROID, appBundleId),
                new BundleId(app2.getId(), ANDROID, app2BundleId)
        ));

        var request = new DirectAppsRequest()
                .withUid(user.getUid())
                .withBundleId(appBundleId)
                .withPlatform(DirectPlatform.ANDROID);
        var actual = getDirectApps(request, status().isOk());
        var expected = List.of(new DirectApp(app, List.of(
                new DirectPlatformBundleId(DirectPlatform.ANDROID, appBundleId))));
        assertThat(actual).isEqualTo(expected);
    }

    private List<DirectApp> getDirectApps(DirectAppsRequest request, ResultMatcher matcher) throws Exception {
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        if (request.getUid() != null) {
            params.set("uid", Objects.toString(request.getUid()));
        }
        if (request.getPlatform() != null) {
            params.set("platform", request.getPlatform().getApiId());
        }
        if (request.getBundleId() != null) {
            params.set("bundle_id", request.getBundleId());
        }
        if (request.getId() != null) {
            params.set("id", Objects.toString(request.getId()));
        }
        MvcResult result = mockMvc.perform(get("/direct/v1/applications")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders())
                .params(params))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(matcher)
                .andReturn();
        return getDefaultMapper()
                .readValue(
                        result.getResponse().getContentAsString(),
                        DirectController.ApplicationsForDirectListWrapper.class)
                .applications;
    }
}
