package ru.yandex.metrika.mobile.push.api.tests;

import io.qameta.allure.Story;
import org.junit.Test;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.PushApiResponse;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.emptyOrNullString;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultApplication;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushSendRequest;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultUserId;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.pushSendRequestWithGroup;

@Story("SendBatch")
public class PushApiSendLogsTest extends PushApiBaseTest {

    @Test
    @Title("Проверка логов batch рассылки")
    public void pushApiSendBatchTest() throws Exception {
        Application application = steps.onApplications().add(defaultUserId(), defaultApplication());
        group = steps.onGroups().add(mockMvc, defaultPushGroup(application.getId()));

        PushApiBatchRequestAdapter sendRequest = defaultPushSendRequest();
        PushApiResponse response = steps.onSend().batch(mockMvc, pushSendRequestWithGroup(sendRequest, group));
        long transferId = response.getTransferId();

        String actualLog = steps.onLogs().get("transfer_" + transferId);
        assertThat("сохранили запрос в лог", actualLog, not(is(emptyOrNullString())));
    }
}
