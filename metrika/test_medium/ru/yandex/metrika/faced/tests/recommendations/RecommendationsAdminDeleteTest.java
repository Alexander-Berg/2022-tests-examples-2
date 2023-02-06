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
public class RecommendationsAdminDeleteTest extends RecommendationsAdminTestBase {
    @Parameterized.Parameter
    public boolean useCreatedId;

    @Parameterized.Parameter(1)
    public ResultMatcher resultMatcher;

    @Parameterized.Parameters
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(new Object[][]{
                {true, status().isOk()},
                {false, status().is4xxClientError()}
        });
    }

    @Test
    public void testDelete() throws Exception {
        RecommendationMeta createdMeta = recommendationSteps.createRecommendationAndExpectSuccess(mockMvc, getDefaultMeta());

        int recommendationId = useCreatedId ? createdMeta.getId() : 0;

        recommendationSteps.deleteRecommendationAndExpectOnSecondStep(mockMvc, recommendationId, resultMatcher);
        if (!useCreatedId) { // need to delete created recommendation
            recommendationSteps.deleteRecommendationAndExpectSuccess(mockMvc, createdMeta.getId());
        }
    }
}
