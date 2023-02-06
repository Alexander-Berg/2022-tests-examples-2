package ru.yandex.metrika.internalapid.api.management.client;

import java.util.Arrays;
import java.util.List;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.internalapid.api.config.CoreControllerConfiguration;

import static org.hamcrest.Matchers.containsStringIgnoringCase;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(SpringJUnit4ClassRunner.class)
@WebAppConfiguration
@ContextConfiguration(classes = {CoreControllerConfiguration.class})
public class CoreControllerTest extends BaseIntapiTest {
    private static final Logger log = LoggerFactory.getLogger(CoreControllerTest.class);
    private static final String IS_INTERNAL_ROLES = "/core/has_internal_roles";

    private final List<Object[]> cases = Arrays.asList(new Object[][]{
            {10L, true},
            {13L, false}
    });

    @Test
    public void test() {
        cases.forEach(curCase -> {
            try {
                MvcResult mvcResult = mockMvc.perform(MockMvcRequestBuilders.get(IS_INTERNAL_ROLES).param("uids", String.valueOf((long) curCase[0])))
                        .andDo(print())
                        .andExpect(status().isOk())
                        .andReturn();
                mockMvc.perform(asyncDispatch(mvcResult))
                        .andExpect(status().isOk())
                        .andExpect(MockMvcResultMatchers.content().string(containsStringIgnoringCase("{\"response\":{\"" + curCase[0] + "\":" + curCase[1] + "}"))
                        )
                        .andReturn();
            } catch (Exception e) {
                log.error("Failed parameters: {}:{}", curCase[0], curCase[1]);
                throw new RuntimeException(e);
            }
        });
    }

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void setup() {
        mockMvcBaseSetup();
    }

}
