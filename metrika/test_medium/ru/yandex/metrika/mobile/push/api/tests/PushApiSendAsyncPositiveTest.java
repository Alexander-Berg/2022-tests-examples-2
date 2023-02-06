package ru.yandex.metrika.mobile.push.api.tests;

import java.util.Collection;
import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableList;
import io.qameta.allure.Story;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.PushApiResponse;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.metrika.mobmet.push.common.model.PushTransferStatus;
import ru.yandex.metrika.mobmet.push.common.transfers.model.PushTransfer;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.core.Is.is;
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

@Story("SendAsync")
@RunWith(Parameterized.class)
public class PushApiSendAsyncPositiveTest extends PushApiBaseTest {

    public static final long ANDROID_DEVICE_ID = 2905865379583152106L;
    public static final long ANOTHER_ANDROID_DEVICE_ID = 431220945225205968L;

    @Parameterized.Parameter
    public PushApiBatchRequestAdapter sendRequest;

    @Parameterized.Parameters()
    public static Collection<Object[]> getParams() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{defaultPushSendRequest()})
                .add(new Object[]{defaultPushSendRequest(Map.of(android.publicName(), defaultPushApiMessage(android)),
                        List.of(defaultGroupAdapter(DEVICE_ID_HASH, 0L)))})
                .add(new Object[]{defaultPushSendRequest(Map.of(android.publicName(), defaultPushApiMessage(android)),
                        List.of(defaultGroupAdapter(DEVICE_ID_HASH, ANDROID_DEVICE_ID)))})
                .add(new Object[]{defaultPushSendRequest(Map.of(android.publicName(), defaultPushApiMessage(android)),
                        List.of(defaultGroupAdapter(DEVICE_ID_HASH, List.of(ANDROID_DEVICE_ID, ANOTHER_ANDROID_DEVICE_ID))))})
                .build();
    }

    @Before
    public void before() throws Exception {
        Application application = steps.onApplications().add(defaultUserId(), defaultApplication());
        steps.onCredentials().add(application.getId());
        group = steps.onGroups().add(mockMvc, defaultPushGroup(application.getId()));
    }

    @Test
    @Title("Асинхронная отправка рассылки")
    public void pushApiSendAsyncPositiveTest() throws Exception {
        PushApiResponse response = steps.onSend().batch(mockMvc, pushSendRequestWithGroup(sendRequest, group));

        long transferId = response.getTransferId();
        PushTransfer pushTransfer = steps.onStatus().receive(mockMvc, transferId);

        assertThat("ответ на /push/v1/send ожидает валидации на push-dispatcher",
                pushTransfer.getStatus(), is(PushTransferStatus.PENDING));
    }
}
