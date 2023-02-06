package ru.yandex.metrika.faced.steps;

import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.metrika.api.management.admin.recommendation.RecommendationMetaListWrapper;
import ru.yandex.metrika.api.management.admin.recommendation.RecommendationMetaWrapper;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationMeta;
import ru.yandex.metrika.api.management.steps.MockMvcSteps;
import ru.yandex.metrika.spring.response.SuccessResponse;
import ru.yandex.qatools.allure.annotations.Step;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static ru.yandex.metrika.util.json.ObjectMappersFactory.getDefaultMapper;

@Component
public class RecommendationSteps extends MockMvcSteps {

    @Autowired
    public RecommendationSteps(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Step("Создать рекомендацию")
    public RecommendationMeta createRecommendationAndExpectSuccess(MockMvc mockMvc, RecommendationMeta meta) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new RecommendationMetaWrapper(meta));
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                post("/internal/admin/recommendation").content(content),
                RecommendationMetaWrapper.class
        ).getRecommendationMeta();
    }

    @Step("Попытаться создать рекомендацию и ожидать ошибку при валидации запроса")
    public void tryCreateRecommendationMetaAndExpect(MockMvc mockMvc, RecommendationMeta meta, ResultMatcher resultMatcher) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new RecommendationMetaWrapper(meta));
        executeAsyncAndExpectOnFirstStep(mockMvc, post("/internal/admin/recommendation").content(content), resultMatcher);
    }

    @Step("Получить рекомендацию {1}")
    public RecommendationMeta getRecommendationAndExpectSuccess(MockMvc mockMvc, int recommendationId) throws Exception {
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                get("/internal/admin/recommendation/{recommendationId}", recommendationId), RecommendationMetaWrapper.class
        ).getRecommendationMeta();
    }

    @Step("Редактировать рекомендацию {1}")
    public RecommendationMeta editRecommendationAndExpectSuccess(MockMvc mockMvc, int recommendationId, RecommendationMeta newMeta) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new RecommendationMetaWrapper(newMeta));
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                put("/internal/admin/recommendation/{recommendationId}", recommendationId).content(content),
                RecommendationMetaWrapper.class
        ).getRecommendationMeta();
    }

    @Step("Удалить рекомендацию {1}")
    public SuccessResponse deleteRecommendationAndExpectSuccess(MockMvc mockMvc, int recommendationId) throws Exception {
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                delete("/internal/admin/recommendation/{recommendationId}", recommendationId),
                SuccessResponse.class
        );
    }

    @Step("Попытаться удалить рекомендацию {1} и ожидать {2} на втором шаге запроса")
    public void deleteRecommendationAndExpectOnSecondStep(MockMvc mockMvc, int recommendationId, ResultMatcher resultMatcher) throws Exception {
        executeAsyncAndExpectOnSecondStep(
                mockMvc,
                delete("/internal/admin/recommendation/{recommendationId}", recommendationId),
                resultMatcher
        );
    }

    @Step("Получить все рекомендации")
    public List<RecommendationMeta> getAllRecommendations(MockMvc mockMvc) throws Exception {
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                get("/internal/admin/recommendations"),
                RecommendationMetaListWrapper.class
        ).getRecommendationMetas();
    }
}
