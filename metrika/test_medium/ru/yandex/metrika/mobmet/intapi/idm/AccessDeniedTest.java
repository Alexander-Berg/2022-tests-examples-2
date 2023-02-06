package ru.yandex.metrika.mobmet.intapi.idm;

import org.junit.Test;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestTvmServices;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class AccessDeniedTest extends AbstractMobmetIntapiTest {

    @Test
    public void noToken() throws Exception {
        mockMvc.perform(get("/idm/fields-info"))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isForbidden());
    }

    @Test
    public void badToken() throws Exception {
        mockMvc.perform(get("/idm/fields-info")
                .headers(TestTvmServices.DIRECT_FRONTEND.getServiceHeaders()))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isForbidden());
    }
}
