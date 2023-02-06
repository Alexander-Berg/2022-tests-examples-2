package ru.yandex.metrika.faced.tests.recommendations;

import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.faced.config.UserRecommendationConfig;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ContextConfiguration(classes = UserRecommendationConfig.class)
@WebAppConfiguration
public class UserRecommendationsTest {

    public static final String USER_RECOMMENDATIONS_BASE_URL = "/internal/management/v1/recommendations";
    @Autowired
    protected WebApplicationContext wac;

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    protected MockMvc mockMvc;

    @Before
    public void before() {
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .build();
    }

    @Test
    public void getRecommendationWithoutCounterIds() throws Exception {
        mockMvc.perform(get(USER_RECOMMENDATIONS_BASE_URL))
                .andExpect(status().isBadRequest()).andReturn();
    }

    @Test
    public void getRecommendationWithIncorrectCounterIds() throws Exception {
        String counterIds = "123,not_interger,other_not_integer";
        mockMvc.perform(
                        get(USER_RECOMMENDATIONS_BASE_URL)
                                .param("counter_ids", counterIds))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isBadRequest());
    }

    @Test
    public void getRecommendationWithTooManyCounterIds() throws Exception {
        String counterIds = IntStream.range(1, 102).mapToObj(String::valueOf).collect(Collectors.joining(","));
        mockMvc.perform(get(USER_RECOMMENDATIONS_BASE_URL).param("counter_ids", counterIds))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isBadRequest());
    }
}
