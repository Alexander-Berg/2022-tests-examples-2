package ru.yandex.metrika.mobmet.intapi.direct;


import java.util.Objects;

import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestData;
import ru.yandex.metrika.mobmet.intapi.common.TestTvmServices;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class DirectControllerEventsTest extends AbstractMobmetIntapiTest {

    @Autowired
    private ApplicationsManageService applicationsManageService;
    @Autowired
    private AuthUtils authUtils;

    @Test
    public void missingParams() throws Exception {
        mockMvc.perform(get("/direct/v1/client_events")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders()))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isBadRequest());
    }

    @Test
    public void invalidUidParams() throws Exception {
        mockMvc.perform(get("/direct/v1/client_events")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders())
                .param("uid", "0")
                .param("app_id", "100"))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isBadRequest());
    }

    @Test
    public void noAccess() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var app = applicationsManageService.createApplication(TestData.defaultApp(), user, user);

        mockMvc.perform(get("/direct/v1/client_events")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders())
                .param("uid", Objects.toString(user.getUid() + 1))
                .param("app_id", Objects.toString(app.getId())))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isNotFound());
    }

    @Test
    public void typedEvents() throws Exception {
        var user = authUtils.getUserByUid(TestData.randomUid());
        var app = applicationsManageService.createApplication(TestData.defaultApp(), user, user);

        mockMvc.perform(get("/direct/v1/typed_events")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders())
                .param("uid", Objects.toString(user.getUid()))
                .param("app_id", Objects.toString(app.getId())))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk());
    }
}
