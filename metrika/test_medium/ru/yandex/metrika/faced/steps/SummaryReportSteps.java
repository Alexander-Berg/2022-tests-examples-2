package ru.yandex.metrika.faced.steps;

import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.api.client.util.Joiner;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.metrika.api.management.client.SummaryReportTelegramLinkController.SummaryReportTelegramSubscriptionWrapper;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportTelegramSubscription;
import ru.yandex.metrika.api.management.client.external.summaryreport.TelegramAuthorizationData;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.steps.MockMvcSteps;
import ru.yandex.qatools.allure.annotations.Step;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;

public class SummaryReportSteps extends MockMvcSteps {
    private final String SUMMARY_REPORT_LINK_URL_PREFIX = "/internal/management/v1/client/summaryreport/";

    public SummaryReportSteps(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Step("Привязать телеграм аккаунт и создать подписку на еженедельные отчеты")
    public SummaryReportTelegramSubscription linkTelegramAndExpectSuccess(
            MockMvc mockMvc,
            String lang,
            TelegramAuthorizationData authorizationData
    ) throws Exception {
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                post(SUMMARY_REPORT_LINK_URL_PREFIX + "telegram/link")
                        .param("lang", lang)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(authorizationData)),
                SummaryReportTelegramSubscriptionWrapper.class
        ).getSubscription();
    }

    @Step("Попытаться привязать телеграмм аккаунт и получить ошибку")
    public void linkTelegramAndExpect(
            MockMvc mockMvc,
            String lang,
            TelegramAuthorizationData authorizationData,
            ResultMatcher resultMatcher
    ) throws Exception {
        executeAsyncAndExpectOnSecondStep(
                mockMvc,
                post(SUMMARY_REPORT_LINK_URL_PREFIX + "telegram/link")
                        .param("lang", lang)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(authorizationData)),
                resultMatcher
        );
    }

    @Step("Отвязать телеграм аккаунт / отписаться от отчетов")
    public void cancelSummarySubscriptionAndExpectSuccess(
            MockMvc mockMvc
    ) throws Exception {
        executeFullAsyncAndExpectSuccess(mockMvc, delete(SUMMARY_REPORT_LINK_URL_PREFIX + "subscription"));
    }

    @Step("Получить подписку")
    public SummaryReportTelegramSubscription getSubscriptionAndExpectSuccess(
            MockMvc mockMvc
    ) throws Exception {
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                get(SUMMARY_REPORT_LINK_URL_PREFIX + "subscription"),
                SummaryReportTelegramSubscriptionWrapper.class
        ).getSubscription();
    }

    @Step("Изменить подписку")
    public SummaryReportTelegramSubscription editSubscriptionAndExpectSuccess(
            MockMvc mockMvc,
            SubscriptionListType listType,
            List<Integer> counterSubscriptions
    ) throws Exception {
        return executeFullAsyncAndExpectSuccess(
                mockMvc,
                put(SUMMARY_REPORT_LINK_URL_PREFIX + "subscription")
                        .param("subscription_type", listType.name())
                        .param("counter_subscriptions", Joiner.on(',').join(counterSubscriptions)),
                SummaryReportTelegramSubscriptionWrapper.class
        ).getSubscription();
    }
}
