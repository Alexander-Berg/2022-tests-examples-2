package ru.yandex.metrika.mobile.push.api.tests;

import java.util.Collection;
import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableList;
import io.qameta.allure.Story;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.PushApiResponse;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.metrika.mobmet.push.common.transfers.model.PushTransfer;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.contains;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultApplication;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultGroupAdapter;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushApiMessage;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushSendRequest;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultUserId;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.pushSendRequestWithGroup;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.DEVICE_ID_HASH;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.android;

@Ignore("MOBMET-15634: move to push-dispatcher")
@Story("SendAsync")
@RunWith(Parameterized.class)
public class PushApiSendAsyncNoCredentialsTest extends PushApiBaseTest {

    public static final long ANDROID_DEVICE_ID = 2905865379583152106L;

    @Parameterized.Parameter
    public PushApiBatchRequestAdapter sendRequest;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters()
    public static Collection<Object[]> getParams() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{defaultPushSendRequest(), "Неверный сертификат или ключ для платформы iOS"})
                .add(new Object[]{defaultPushSendRequest(
                        Map.of(android.publicName(), defaultPushApiMessage(android)),
                        List.of(defaultGroupAdapter(DEVICE_ID_HASH, ANDROID_DEVICE_ID))),
                        "Неверный сертификат или ключ для платформы android"})
                .build();
    }

    @Before
    public void before() throws Exception {
        Application application = steps.onApplications().add(defaultUserId(), defaultApplication());
        group = steps.onGroups().add(mockMvc, defaultPushGroup(application.getId()));
    }

    @Test
    @Title("Асинхронная отправка рассылки без сертификата")
    public void pushApiSendAsyncNoCredentialsTest() throws Exception {
        PushApiResponse response = steps.onSend().batch(mockMvc, pushSendRequestWithGroup(sendRequest, group));

        long transferId = response.getTransferId();
        steps.waitUntilFastValidationComplete(mockMvc, transferId);
        PushTransfer pushTransfer = steps.onStatus().receive(mockMvc, transferId);

        assertThat("ответ на /push/v1/send содержит ожидаемую ошибку валидации",
                pushTransfer.getErrors(), contains(message));
    }

}
