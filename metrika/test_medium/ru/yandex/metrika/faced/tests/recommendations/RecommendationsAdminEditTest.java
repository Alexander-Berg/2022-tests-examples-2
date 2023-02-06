package ru.yandex.metrika.faced.tests.recommendations;

import java.util.Arrays;
import java.util.Collection;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationMeta;

@RunWith(Parameterized.class)
public class RecommendationsAdminEditTest extends RecommendationsAdminTestBase {

    private int recommendationId;

    @Parameterized.Parameter
    public RecommendationMeta newMeta;

    @Before
    public void setup() throws Exception {
        recommendationId = recommendationSteps.createRecommendationAndExpectSuccess(mockMvc, getDefaultMeta()).getId();
    }

    @Parameterized.Parameters
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(new Object[][]{
                {getDefaultMeta()},
                {getDefaultMeta().withPriority(null)},
                {getDefaultMeta().withDashboardText(null)},
                {getDefaultMeta().withName(null)},
                {getDefaultMeta().withRecommendationActionKind(null)}
        });
    }

    @Test
    public void testEdit() throws Exception {
        recommendationSteps.editRecommendationAndExpectSuccess(mockMvc, recommendationId, newMeta);
    }

    @After
    public void cleanUp() throws Exception {
        recommendationSteps.deleteRecommendationAndExpectSuccess(mockMvc, recommendationId);
    }

}
