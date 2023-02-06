package ru.yandex.metrika.mobmet.intapi;

import org.junit.Test;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;

import static org.hamcrest.Matchers.equalTo;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class PingTest extends AbstractMobmetIntapiTest {
    @Test
    public void test() throws Exception {
        mockMvc.perform(get("/ping"))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("success", equalTo(true)));
    }
}
