package ru.yandex.metrika.mobile.push.api.steps;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.IntStream;

import com.google.common.collect.ImmutableMap;
import org.apache.commons.lang3.RandomUtils;
import org.apache.commons.lang3.StringUtils;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.DevicesGroupAdapter;
import ru.yandex.metrika.mobmet.push.api.model.PushApiActionAdapter;
import ru.yandex.metrika.mobmet.push.api.model.PushApiMessageAdapter;
import ru.yandex.metrika.mobmet.push.api.model.PushGroupAdapter;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiNotificationAdapter;
import ru.yandex.metrika.mobmet.push.common.model.IdType;
import ru.yandex.metrika.segments.apps.misc.PushPlatform;

import static com.google.common.collect.Lists.newArrayList;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static java.util.Collections.singletonMap;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.RandomStringUtils.randomAlphanumeric;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.android;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.iOS;


public class TestData {

    private static final int MAX_COLOR_SIZE = 8;

    private static final int COLOR_POSITION_SIZE = 2;

    private static final String PLACEHOLDER = "0";

    public static final Long CLIENT_TRANSFER_ID = 777L;

    private static final String DEEP_LINK = "Deep link ";

    private static final String PUSH_GROUP_BASE_NAME = "Тестовая группа";

    private static final String PUSH_GROUP_TAG = "Тестовый тег";

    private static final String TEXT = "Текст ";

    private static final String TITLE = "Заголовок ";

    private static final String URL_ADDRESS = "https://example.com/";

    private static final int RANDOM_STRING_LENGTH = 10;

    private static final int FOOD_APP_CATEGORY = 91;

    public static long defaultUserId() {
        return 1L;
    }

    public static Application defaultApplication() {
        return Application.builder()
                .setId(nextInt())
                .setName("test")
                .setCategory(FOOD_APP_CATEGORY)
                .build();
    }

    public static PushGroupAdapter defaultPushGroup(long applicationId) {
        return new PushGroupAdapter(nextUnsignedLong(), applicationId, getPushGroupName(), 500);
    }

    public static PushGroupAdapter updatedPushGroup(long groupId, PushGroupAdapter group) {
        return new PushGroupAdapter(groupId, group.getAppId(), getPushGroupName(), 500);
    }

    public static PushApiBatchRequestAdapter defaultPushSendRequest() {
        return defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)));
    }

    public static PushApiBatchRequestAdapter defaultPushSendRequest(Map<String, PushApiMessageAdapter> messages) {
        return defaultPushSendRequest(messages, singletonList(defaultGroupAdapter(IdType.IOS_IFA)));
    }

    public static PushApiBatchRequestAdapter defaultPushSendRequest(List<DevicesGroupAdapter> devices) {
        return defaultPushSendRequest(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), devices);
    }

    public static PushApiBatchRequestAdapter defaultPushSendRequest(Map<String, PushApiMessageAdapter> messages,
                                                                    List<DevicesGroupAdapter> devices) {
        return new PushApiBatchRequestAdapter(nextUnsignedLong(), nextUnsignedLong(), randomPushTag(),
                List.of(new PushApiNotificationAdapter(messages, devices)));
    }

    public static PushApiBatchRequestAdapter pushSendRequestWithGroup(PushApiBatchRequestAdapter push, PushGroupAdapter group) {
        return new PushApiBatchRequestAdapter(push.getClientTransferId(), group.getId(), push.getTag(), push.getBatch());
    }

    public static PushApiBatchRequestAdapter defaultPushSendBatchRequest(PushGroupAdapter group) {
        return defaultPushSendBatchRequest(group, CLIENT_TRANSFER_ID);
    }

    public static PushApiBatchRequestAdapter defaultPushSendBatchRequest(PushGroupAdapter group, Long clientTransferId) {
        return new PushApiBatchRequestAdapter(clientTransferId, group.getId(), randomPushTag(), asList(
                new PushApiNotificationAdapter(singletonMap(iOS.publicName(), defaultPushApiMessage(iOS)), singletonList(defaultGroupAdapter(IdType.IOS_IFA))),
                new PushApiNotificationAdapter(singletonMap(android.publicName(), defaultPushApiMessage(android)), singletonList(defaultGroupAdapter(IdType.GOOGLE_AID)))
        ));
    }

    public static DevicesGroupAdapter defaultGroupAdapter(IdType idType) {
        return defaultGroupAdapter(idType, randomDeviceId(idType));
    }

    public static DevicesGroupAdapter defaultGroupAdapter(IdType idType, String deviceId) {
        return defaultGroupAdapter(idType, singletonList(deviceId));
    }

    public static DevicesGroupAdapter defaultGroupAdapter(IdType idType, long deviceId) {
        return defaultGroupAdapter(idType, singletonList(String.valueOf(deviceId)));
    }

    public static <T> DevicesGroupAdapter defaultGroupAdapter(IdType idType, List<T> devicesIds) {
        return new DevicesGroupAdapter(idType, devicesIds.stream().map(Object::toString).collect(toList()));
    }

    public static PushApiMessageAdapter defaultPushApiMessage(PushPlatform platform) {
        return new PushApiMessageAdapter(false, defaultPushApiActionAdapter(), defaultMessageContent(platform));
    }

    public static PushApiActionAdapter defaultPushApiActionAdapter() {
        return new PushApiActionAdapter(randomUrl(), randomDeepLink());
    }

    public static Map<String, Object> defaultMessageContent(PushPlatform platform) {
        return switch (platform) {
            case iOS -> defaultIosMessage();
            case android -> defaultAndroidMessage();
            case WindowsPhone -> defaultWindowsMessage();
        };
    }

    private static Map<String, Object> defaultIosMessage() {
        return ImmutableMap.<String, Object>builder()
                .put("title", randomTitle())
                .put("text", randomText())
                .put("badge", nextInt(200))
                .put("expiration", nextInt())
                .put("data", randomAlphanumeric(1000))
                .put("sound", "default")
                .put("mutable_content", nextInt(2))
                .build();
    }

    private static Map<String, Object> defaultAndroidMessage() {
        return ImmutableMap.<String, Object>builder()
                .put("title", randomTitle())
                .put("text", randomText())
                .put("icon", String.valueOf(nextInt()))
                .put("icon_background", randomColor())
                .put("image", randomUrl())
                .put("data", randomAlphanumeric(1000))
                .put("sound", "default")
                .put("vibration", newArrayList(nextInt(), nextInt()))
                .put("led_color", randomColor(false))
                .put("led_interval", nextInt())
                .put("led_pause_interval", nextInt())
                .put("priority", nextInt(5) - 2) // from -2 to 2
                .put("visibility", "public")
                .put("urgency", "normal")
                .put("collapse_key", nextInt())
                .put("time_to_live", nextInt())
                .put("time_to_live_on_device", nextInt())
                .put("banner", randomUrl())
                .put("channel_id", randomTitle())
                .build();
    }

    private static Map<String, Object> defaultWindowsMessage() {
        return ImmutableMap.of(
                "title", randomTitle(),
                "text", randomText());
    }

    public static List<String> randomDevicesIds(IdType idType, int count) {
        return IntStream.range(0, count)
                .mapToObj(i -> randomDeviceId(idType))
                .collect(toList());
    }

    public static String randomDeviceId(IdType idType) {
        return switch (idType) {
            case IOS_IFA, IOS_IFV, GOOGLE_AID, HUAWEI_OAID -> UUID.randomUUID().toString();
            case ANDROID_PUSH_TOKEN, HUAWEI_PUSH_TOKEN -> randomAlphanumeric(165);
            case IOS_PUSH_TOKEN -> randomAlphanumeric(32);
            case DEVICE_ID_HASH -> String.valueOf(nextInt());
        };
    }

    public static String getPushGroupName() {
        return PUSH_GROUP_BASE_NAME + " " + randomAlphanumeric(RANDOM_STRING_LENGTH);
    }

    public static String randomColor() {
        return randomColor(RandomUtils.nextBoolean());
    }

    public static String randomColor(boolean withAlpha) {
        String hexInt = Integer.toHexString(nextInt()).toUpperCase();

        if (hexInt.length() < MAX_COLOR_SIZE) {
            hexInt = StringUtils.repeat(PLACEHOLDER, MAX_COLOR_SIZE - hexInt.length()) + hexInt;
        }

        return "#" + (withAlpha ? hexInt : hexInt.substring(COLOR_POSITION_SIZE));
    }

    public static String randomPushTag() {
        return PUSH_GROUP_TAG + " " + randomAlphanumeric(RANDOM_STRING_LENGTH);
    }

    public static long randomClientTransferId() {
        return nextUnsignedLong();
    }

    public static String randomDeepLink() {
        return DEEP_LINK + randomAlphanumeric(RANDOM_STRING_LENGTH);
    }

    private static String randomUrl() {
        return URL_ADDRESS + randomAlphanumeric(RANDOM_STRING_LENGTH);
    }

    private static String randomTitle() {
        return TITLE + randomAlphanumeric(RANDOM_STRING_LENGTH);
    }

    private static String randomText() {
        return TEXT + randomAlphanumeric(500);
    }

    private static int nextInt(int maxValue) {
        return RandomUtils.nextInt(0, maxValue);
    }

    private static int nextInt() {
        return nextInt(Integer.MAX_VALUE);
    }

    private static long nextUnsignedLong() {
        return RandomUtils.nextLong(0, Long.MAX_VALUE);
    }

}
