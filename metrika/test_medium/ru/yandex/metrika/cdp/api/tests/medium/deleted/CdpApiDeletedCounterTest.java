package ru.yandex.metrika.cdp.api.tests.medium.deleted;

import org.junit.Test;
import org.springframework.security.test.context.support.WithUserDetails;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.web.WebAppConfiguration;

import ru.yandex.metrika.cdp.api.spring.CdpApiTestConfig;
import ru.yandex.metrika.cdp.api.tests.medium.AbstractCdpApiTest;
import ru.yandex.metrika.cdp.api.users.TestUsers;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ContextConfiguration(classes = CdpApiTestConfig.class)
@WebAppConfiguration
@WithUserDetails(TestUsers.SIMPLE_USER_NAME)
public class CdpApiDeletedCounterTest extends AbstractCdpApiTest {

    private static final String COUNTER_PATH_TEMPLATE = "/cdp/api/v1/test/counter/{counterId}/noop";
    private static final String STAT_PATH_TEMPLATE = "/cdp/api/v1/test/stat/noop?ids={counterId}";

    private int counterId;

    @Test
    public void testNotExistingCounter() throws Exception {
        mockMvc.perform(get(COUNTER_PATH_TEMPLATE, Integer.MAX_VALUE)).andExpect(status().isNotFound());
    }

    @Test
    public void testNotExistingStat() throws Exception {
        mockMvc.perform(get(STAT_PATH_TEMPLATE, Integer.MAX_VALUE)).andExpect(status().isNotFound());
    }

    @Test
    public void testExistingCounter() throws Exception {
        counterId = createCounter();
        mockMvc.perform(get(COUNTER_PATH_TEMPLATE, counterId)).andExpect(status().isOk());
    }

    @Test
    public void testExistingStat() throws Exception {
        counterId = createCounter();
        mockMvc.perform(get(STAT_PATH_TEMPLATE, counterId)).andExpect(status().isOk());
    }

    @Test
    public void testDeletedCounter() throws Exception {
        counterId = createCounter();
        deleteCounter(counterId);
        mockMvc.perform(get(COUNTER_PATH_TEMPLATE, counterId)).andExpect(status().isNotFound());
    }

    @Test
    public void testDeletedStat() throws Exception {
        counterId = createCounter();
        deleteCounter(counterId);
        mockMvc.perform(get(STAT_PATH_TEMPLATE, counterId)).andExpect(status().isNotFound());
    }
}
