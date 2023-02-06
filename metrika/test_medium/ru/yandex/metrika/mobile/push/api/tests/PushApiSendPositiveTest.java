package ru.yandex.metrika.mobile.push.api.tests;

import java.util.Collection;
import java.util.Map;

import com.google.common.collect.ImmutableList;
import io.qameta.allure.Story;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.PushApiMessageAdapter;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static java.util.Collections.singletonMap;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultApplication;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultGroupAdapter;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushApiActionAdapter;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushApiMessage;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushSendRequest;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultUserId;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.pushSendRequestWithGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.randomDevicesIds;
import static ru.yandex.metrika.mobmet.push.common.campaigns.validation.FieldKey.APNS_COLLAPSE_ID;
import static ru.yandex.metrika.mobmet.push.common.campaigns.validation.FieldKey.TEXT;
import static ru.yandex.metrika.mobmet.push.common.campaigns.validation.FieldKey.TITLE;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.DEVICE_ID_HASH;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.GOOGLE_AID;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.IOS_IFA;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.IOS_IFV;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.android;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.iOS;

@Story("Send")
@RunWith(Parameterized.class)
public class PushApiSendPositiveTest extends PushApiBaseTest {

    private static final int ALLOWED_MESSAGE_LENGTH = 2048;

    private static final int DEVICES_LIMIT = 250000;

    @Parameterized.Parameter
    public PushApiBatchRequestAdapter sendRequest;

    @Parameterized.Parameters()
    public static Collection<Object[]> getParams() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{defaultPushSendRequest()})
                .add(new Object[]{defaultPushSendRequest(singletonList(defaultGroupAdapter(DEVICE_ID_HASH, randomDevicesIds(DEVICE_ID_HASH, DEVICES_LIMIT))))})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IOS_IFA)))})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IOS_IFV)))})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), new PushApiMessageAdapter(true, defaultPushApiActionAdapter(), singletonMap(TEXT.getName(), null))))})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(),
                        new PushApiMessageAdapter(true, null, singletonMap(APNS_COLLAPSE_ID.getName(), "AppMetCollapseId_3246214362154365214365214356_25371253"))))})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(),
                        new PushApiMessageAdapter(false, null, singletonMap(TEXT.getName(), RandomStringUtils.randomAlphanumeric(ALLOWED_MESSAGE_LENGTH)))))})
                .add(new Object[]{defaultPushSendRequest(singletonMap(android.publicName(),
                        new PushApiMessageAdapter(false, null,
                                Map.of(TITLE.getName(), "Android", TEXT.getName(), RandomStringUtils.randomAlphanumeric(ALLOWED_MESSAGE_LENGTH)))), singletonList(defaultGroupAdapter(GOOGLE_AID)))})
                .build();
    }

    @Before
    public void before() throws Exception {
        Application application = steps.onApplications().add(defaultUserId(), defaultApplication());
        group = steps.onGroups().add(mockMvc, defaultPushGroup(application.getId()));
    }

    @Test
    @Title("Отправка рассылки")
    public void pushApiSendPositiveTest() throws Exception {
        steps.onSend().batch(mockMvc, pushSendRequestWithGroup(sendRequest, group));
    }
}
