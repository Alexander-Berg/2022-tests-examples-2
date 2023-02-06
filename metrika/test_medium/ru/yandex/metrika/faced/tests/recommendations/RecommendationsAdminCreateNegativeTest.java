package ru.yandex.metrika.faced.tests.recommendations;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationMeta;

import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(Parameterized.class)
public class RecommendationsAdminCreateNegativeTest extends RecommendationsAdminTestBase {
    @Parameterized.Parameter
    public RecommendationMeta createMeta;

    @Parameterized.Parameter(1)
    public ResultMatcher resultMatcher;

    @Parameterized.Parameters
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(new Object[][]{
                {getDefaultMeta().withDaysForLive(-1), status().is4xxClientError()},
                {getDefaultMeta().withPriority(-10), status().is4xxClientError()},
                {getDefaultMeta().withFrequenceShow(-1), status().is4xxClientError()}
        });
    }

    @Test
    public void testCreateNegative() throws Exception {
        recommendationSteps.tryCreateRecommendationMetaAndExpect(mockMvc, createMeta, resultMatcher);
    }
}
