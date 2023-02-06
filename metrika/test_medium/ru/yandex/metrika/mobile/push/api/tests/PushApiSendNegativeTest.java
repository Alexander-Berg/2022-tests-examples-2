package ru.yandex.metrika.mobile.push.api.tests;

import java.util.Collection;

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

import static java.lang.String.format;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static java.util.Collections.singletonMap;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultApplication;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultGroupAdapter;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushApiMessage;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushSendRequest;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultUserId;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.pushSendRequestWithGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.randomDevicesIds;
import static ru.yandex.metrika.mobmet.push.common.campaigns.validation.FieldKey.APNS_COLLAPSE_ID;
import static ru.yandex.metrika.mobmet.push.common.campaigns.validation.FieldKey.TEXT;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.DEVICE_ID_HASH;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.IOS_IFA;
import static ru.yandex.metrika.mobmet.push.common.model.IdType.IOS_IFV;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.WindowsPhone;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.android;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.iOS;

@Story("Send")
@RunWith(Parameterized.class)
public class PushApiSendNegativeTest extends PushApiBaseTest {

    /**
     * Сейчас максимальный допустимый размер payload для Android и iOS равен 4096 байтам.
     * Но необходимо еще оставить резерв на остальные поля и издержки протокола
     */
    private static final int TOO_LARGE_MESSAGE_LENGTH = 4096;

    private static final int DEVICES_LIMIT = 250000;

    @Parameterized.Parameter
    public PushApiBatchRequestAdapter sendRequest;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters()
    public static Collection<Object[]> getParams() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{defaultPushSendRequest(singletonMap(WindowsPhone.publicName(), defaultPushApiMessage(WindowsPhone))),
                        "Поддерживаются только платформы iOS, android"})
                .add(new Object[]{defaultPushSendRequest(asList(defaultGroupAdapter(DEVICE_ID_HASH, randomDevicesIds(DEVICE_ID_HASH, DEVICES_LIMIT)),
                        defaultGroupAdapter(IOS_IFA, randomDevicesIds(IOS_IFA, 1)))),
                        "Превышено максимальное число устройств в одной рассылке"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(android.publicName(), defaultPushApiMessage(android)), singletonList(defaultGroupAdapter(IOS_IFA))),
                        "Для того, чтобы использовать тип идентификатора ios_ifa необходимо задать сообщение для платформы iOS"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IOS_IFA, ""))),
                        "Некорректное значение ios_ifa: ''"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IOS_IFA, "null"))),
                        "Некорректное значение ios_ifa: 'null'"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(android.publicName(), defaultPushApiMessage(android)), singletonList(defaultGroupAdapter(IOS_IFV))),
                        "Для того, чтобы использовать тип идентификатора ios_ifv необходимо задать сообщение для платформы iOS"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IOS_IFV, ""))),
                        "Некорректное значение ios_ifv: ''"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IOS_IFV, "null"))),
                        "Некорректное значение ios_ifv: 'null'"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(),
                        new PushApiMessageAdapter(true, null, singletonMap(APNS_COLLAPSE_ID.getName(), "AppMetCollapseId_3246214362154365214365214356_253712537215376235762537")))),
                        format("Некорректное сообщение для платформы iOS. Превышена длина поля %s", APNS_COLLAPSE_ID.getName())})
                .add(new Object[]{defaultPushSendRequest(singletonMap(android.publicName(),
                        new PushApiMessageAdapter(false, null, singletonMap(TEXT.getName(), RandomStringUtils.randomAlphanumeric(TOO_LARGE_MESSAGE_LENGTH))))),
                        "Размер сообщения превышает допустимый лимит"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(),
                        new PushApiMessageAdapter(false, null, singletonMap(TEXT.getName(), RandomStringUtils.randomAlphanumeric(TOO_LARGE_MESSAGE_LENGTH))))),
                        "Размер сообщения превышает допустимый лимит"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(android.publicName(),
                        new PushApiMessageAdapter(false, null, singletonMap(TEXT.getName(), null)))),
                        "Обязательное поле не может быть пустым"})
                .add(new Object[]{defaultPushSendRequest(singletonMap(iOS.publicName(),
                        new PushApiMessageAdapter(false, null, singletonMap(TEXT.getName(), null)))),
                        "Обязательное поле не может быть пустым"})
                .build();
    }

    @Before
    public void before() throws Exception {
        Application application = steps.onApplications().add(defaultUserId(), defaultApplication());
        group = steps.onGroups().add(mockMvc, defaultPushGroup(application.getId()));
    }

    @Test
    @Title("Отправка рассылки с ошибкой")
    public void pushApiSendNegativeTest() throws Exception {
        PushApiBatchRequestAdapter request = pushSendRequestWithGroup(sendRequest, group);
        steps.onSend().batchWithMessage(mockMvc, request, status().isBadRequest(), message);
    }
}
