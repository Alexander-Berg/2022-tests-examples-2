package ru.yandex.metrika.mobile.push.api.tests;

import io.qameta.allure.Story;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.qatools.allure.annotations.Title;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.notNullValue;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultApplication;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushSendBatchRequest;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultUserId;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.randomClientTransferId;

@Story("SendBatch")
public class PushApiSendBatchTest extends PushApiBaseTest {

    @Before
    public void before() throws Exception {
        Application application = steps.onApplications().add(defaultUserId(), defaultApplication());
        group = steps.onGroups().add(mockMvc, defaultPushGroup(application.getId()));
    }

    @Test
    @Title("Отправка batch рассылки")
    public void pushApiSendBatchTest() throws Exception {
        steps.onSend().batch(mockMvc, defaultPushSendBatchRequest(group));
    }

    @Test
    @Title("Дублирование client_transfer_id при отправке batch рассылки")
    public void pushApiSendBatchClientTransferIdDuplicateTest() throws Exception {
        // Берём произвольный client_transfer_id
        PushApiBatchRequestAdapter sendRequest = defaultPushSendBatchRequest(group, randomClientTransferId());
        assertThat(sendRequest.getClientTransferId(), notNullValue());

        // Проверяем, что такого client_transfer_id ещё нет
        steps.onStatus().receiveWithError(mockMvc, sendRequest.getGroupId(),
                sendRequest.getClientTransferId(), status().isNotFound());

        // Делаем по нему рассылку
        steps.onSend().batch(mockMvc, sendRequest);

        // Ожидаем, что у рассылки теперь можно узнать статус по client_transfer_id
        steps.onStatus().receive(mockMvc, sendRequest.getGroupId(), sendRequest.getClientTransferId());

        // Пробуем сделать повторную рассылку по такому же client_transfer_id и получаем ошибку
        String errorMessage = format("В группе %d уже имеется client_transfer_id = %d",
                sendRequest.getGroupId(), sendRequest.getClientTransferId());
        steps.onSend().batchWithMessage(mockMvc, sendRequest, status().isBadRequest(), errorMessage);
    }

}
