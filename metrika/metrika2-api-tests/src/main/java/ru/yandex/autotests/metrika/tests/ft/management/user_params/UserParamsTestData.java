package ru.yandex.autotests.metrika.tests.ft.management.user_params;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.utils.CsvSerializer;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploading;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static com.google.common.collect.ImmutableList.of;
import static com.google.common.collect.Lists.transform;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction.DELETE_KEYS;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction.UPDATE;

/**
 * Created by ava1on on 07.04.17.
 */
public class UserParamsTestData {
    private static final String COLUMN_USER_ID = "userid";
    private static final String COLUMN_CLIENT_ID = "clientid";
    private static final String COLUMN_KEY = "key";
    private static final String COLUMN_VALUE = "value";
    private static final List<String> COMMON_COLUMNS = of(COLUMN_KEY, COLUMN_VALUE);

    public final static Map<String, String> VALUES = ImmutableMap.<String, String>builder()
            .put(COLUMN_USER_ID, "1149398411465467809")
            .put(COLUMN_CLIENT_ID, "28375672")
            .put(COLUMN_KEY, "gender")
            .put(COLUMN_VALUE, "M")
            .build();

    public final static Map<String, String> VALUES_6_LEVEL = ImmutableMap.<String, String>builder()
            .put(COLUMN_USER_ID, "1149398411465467809")
            .put(COLUMN_CLIENT_ID, "28375672")
            .put(COLUMN_KEY, "level1.level2.level3.level4.level5.level6")
            .put(COLUMN_VALUE, "value_value")
            .build();

    public final static List<List<String>> DELETE_VALUES = ImmutableList.of(of("key"), of("gender"));

    public static CsvSerializer serializer = new CsvSerializer();

    public static String createContent1Row(UserParamsUploadingContentIdType contentIdType) {
        List<String> header = getHeader(contentIdType);
        return serializer.serialize(ImmutableList.of(
                header,
                transform(header, VALUES::get)
        ));
    }

    public static String createContent2Rows(UserParamsUploadingContentIdType contentIdType) {
        List<String> header = getHeader(contentIdType);

        return serializer.serialize(of(
                header,
                transform(header, VALUES::get),
                transform(header, VALUES_6_LEVEL::get)
        ));
    }

    public static Object[] createBaseContent(UserParamsUploadingContentIdType contentIdType) {
        List<String> header = getHeader(contentIdType);
        return createContent("базовый", header, false);
    }

    public static Object[] createContentWithoutHeader(UserParamsUploadingContentIdType contentIdType) {
        List<String> header = getHeader(contentIdType);

        return toArray(
                "Без заголовка",
                serializer.serialize(of(transform(header, VALUES::get))),
                UPDATE
        );
    }

    public static Object[] createContentWith6LevelParameter(UserParamsUploadingContentIdType contentIdType) {
        List<String> header = getHeader(contentIdType);
        return createContent("Параметр 6го уровня", header, true);
    }

    public static Object[] createContentWithShuffledColumns(UserParamsUploadingContentIdType contentIdType) {
        List<String> shuffledHeader = new ArrayList<>(getHeader(contentIdType));
        Collections.shuffle(shuffledHeader);

        return createContent("столбцы в другом порядке", shuffledHeader, false);
    }

    public static Object[] createEmptyContent(IExpectedError error) {
        return toArray("пустой файл", error, StringUtils.EMPTY);
    }

    public static Object[] createContentWithoutData(IExpectedError error,
                                                    UserParamsUploadingContentIdType contentIdType) {
        List<String> header = getHeader(contentIdType);
        return toArray("файл без данных",
                error,
                serializer.serialize(of(header))
        );
    }

    public static Object[] createDeleteContent() {
        return toArray("удаление ключей", serializer.serialize(DELETE_VALUES), DELETE_KEYS);
    }

    public static Object[] createDeleteContentWithoutData(IExpectedError error) {
        return toArray("файл для удаления без данных", error, COLUMN_KEY);
    }

    private static List<String> getHeader(UserParamsUploadingContentIdType contentIdType) {
        String uploadType = COLUMN_USER_ID;
        if(contentIdType.equals(UserParamsUploadingContentIdType.CLIENT_ID))
            uploadType = COLUMN_CLIENT_ID;

        return ImmutableList.<String>builder()
                .add(uploadType)
                .addAll(COMMON_COLUMNS)
                .build();
    }

    private static Object[] createContent(String description, List<String> header, Boolean level6) {
        Map<String, String> values = getValues(level6);

        return toArray(
                description,
                serializer.serialize(of(header, transform(header, values::get))),
                UPDATE
        );
    }

    private static Map<String, String> getValues(Boolean level6) {
        if (level6)
            return VALUES_6_LEVEL;
        return VALUES;
    }

    public static UserParamsUploading getUploadingToChange(UserParamsUploading uploading, String newComment) {
        return new UserParamsUploading()
                .withId(uploading.getId())
                .withLineQuantity(uploading.getLineQuantity())
                .withAction(uploading.getAction())
                .withComment(newComment)
                .withContentIdType(uploading.getContentIdType());
    }

    public static UserParamsUploading getExpectedUploading(String content, UserParamsUploadingAction action,
                                                           UserParamsUploadingContentIdType contentIdType) {
        String[] lines = content.split("\n");
        int number = lines.length;
        if (lines[0].contains("key"))
            --number;

        return new UserParamsUploading()
                .withAction(action)
                .withComment("data.csv")
                .withLineQuantity((long)number)
                .withContentIdType(contentIdType);
    }
}