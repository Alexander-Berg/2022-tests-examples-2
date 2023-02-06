package ru.yandex.metrika.faced.tests.recommendations;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationMeta;

public class RecommendationsAdminGetAllTest extends RecommendationsAdminTestBase {

    private static final int TEST_METAS_COUNT = 5;

    private final List<RecommendationMeta> metas = new ArrayList<>(TEST_METAS_COUNT);

    @Before
    public void setup() throws Exception {
        for (int i = 0; i < TEST_METAS_COUNT; ++i) {
            metas.add(recommendationSteps.createRecommendationAndExpectSuccess(mockMvc, getDefaultMeta()));
        }
    }

    @Test
    public void testGetAll() throws Exception {
        List<RecommendationMeta> recommendationMetas = recommendationSteps.getAllRecommendations(mockMvc);
        Map<Integer, RecommendationMeta> id2meta = recommendationMetas.stream().collect(Collectors.toMap(RecommendationMeta::getId, Function.identity()));

        for (RecommendationMeta meta : metas) {
            checkForEqualityWithoutId(id2meta.get(meta.getId()), meta);
        }
    }

    @After
    public void cleanUp() throws Exception {
        for (RecommendationMeta meta : metas) {
            recommendationSteps.deleteRecommendationAndExpectSuccess(mockMvc, meta.getId());
        }
    }
}
