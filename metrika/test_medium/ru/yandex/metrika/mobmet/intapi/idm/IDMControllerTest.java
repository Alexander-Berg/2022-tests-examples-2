package ru.yandex.metrika.mobmet.intapi.idm;

import org.junit.Test;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestTvmServices;
import ru.yandex.metrika.util.io.IOUtils;

import static org.hamcrest.Matchers.equalTo;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class IDMControllerTest extends AbstractMobmetIntapiTest {

    @Test
    public void info() throws Exception {
        mockMvc.perform(get("/idm/info")
                .headers(TestTvmServices.IDM.getServiceHeaders()))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk())
                .andExpect(content()
                        .json(IOUtils.resourceAsString(IDMControllerTest.class, "testdata/idm_fields_info.json")));
    }

    @Test
    public void fieldInfo() throws Exception {
        mockMvc.perform(get("/idm/fields-info")
                .headers(TestTvmServices.IDM.getServiceHeaders()))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("code", equalTo(0)));
    }

    @Test
    public void addRole() throws Exception {
        mockMvc.perform(post("/idm/add-role")
                .headers(TestTvmServices.IDM.getServiceHeaders())
                .param("login", "crow")
                .param("role", "{\"appmetrica\":\"appmetrica_yamanager\"}")
                .param("fields", "{\"passport-login\":\"yndx-crow\"}"))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("code", equalTo(0)));
    }
}
