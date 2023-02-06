package ru.yandex.metrika.faced.tests.recommendations;

import java.util.Arrays;
import java.util.Collection;

import org.junit.After;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationMeta;


@RunWith(Parameterized.class)
public class RecommendationsAdminCreateTest extends RecommendationsAdminTestBase {

    private int createdRecommendationId;

    @Parameterized.Parameter
    public RecommendationMeta createMeta;

    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {getDefaultMeta()},
                {getDefaultMeta().withEmailTemplate(null)},
                {getDefaultMeta().withDashboardText(null)},
                {getDefaultMeta().withShowForTypes(null)}
        });
    }

    @Test
    public void createMeta() throws Exception {
        RecommendationMeta postMeta = recommendationSteps.createRecommendationAndExpectSuccess(mockMvc, createMeta);
        createdRecommendationId = postMeta.getId();

        checkForEqualityWithoutId(postMeta, createMeta);

        RecommendationMeta getMeta = recommendationSteps.getRecommendationAndExpectSuccess(mockMvc, postMeta.getId());
        checkForEqualityWithoutId(getMeta, createMeta);
    }

    @After
    public void cleanUp() throws Exception {
        recommendationSteps.deleteRecommendationAndExpectSuccess(mockMvc, createdRecommendationId);
    }
}
