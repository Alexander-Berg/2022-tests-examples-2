package ru.yandex.autotests.metrika.data.management.v1.offlineconversion;

import java.util.List;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;

import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_CLIENT_ID;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_CURRENCY;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_DATE_TIME;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_PRICE;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_TARGET;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_USER_ID;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_YCLID;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_CALL_MISSED;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_CALL_TRACKER_URL;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_FIRST_TIME_CALLER;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_HOLD_DURATION;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_PHONE_NUMBER;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_STATIC_CALL;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_TAG;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_TALK_DURATION;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_URL;

/**
 * @author zgmnkv
 */
public class OfflineConversionType<T extends OfflineConversionUploadingData> {

    public static final OfflineConversionType<BasicOfflineConversionUploadingData> BASIC = new OfflineConversionType<>(
            "BASIC",
            of(COLUMN_TARGET),
            "/management/v1/counter/%s/offline_conversions/upload",
            "/management/v1/counter/%s/offline_conversions/uploading/%s",
            "/management/v1/counter/%s/offline_conversions/uploadings",
            "/management/v1/counter/%d/offline_conversions/extended_threshold",
            BasicOfflineConversionUploadingData.class,
            BasicOfflineConversionUploadingData::new);

    public static final OfflineConversionType<CallsOfflineConversionUploadingData> CALLS = new OfflineConversionType<>(
            "CALLS",
            of(
                    COLUMN_PHONE_NUMBER,
                    COLUMN_TALK_DURATION,
                    COLUMN_HOLD_DURATION,
                    COLUMN_CALL_MISSED,
                    COLUMN_TAG,
                    COLUMN_FIRST_TIME_CALLER,
                    COLUMN_URL,
                    COLUMN_CALL_TRACKER_URL,
                    COLUMN_STATIC_CALL
            ),
            "/management/v1/counter/%s/offline_conversions/upload_calls",
            "/management/v1/counter/%s/offline_conversions/calls_uploading/%s",
            "/management/v1/counter/%s/offline_conversions/calls_uploadings",
            "/management/v1/counter/%d/offline_conversions/calls_extended_threshold",
            CallsOfflineConversionUploadingData.class,
            CallsOfflineConversionUploadingData::new);

    private static final OfflineConversionType<?>[] VALUES = { BASIC, CALLS };

    public static OfflineConversionType<?>[] values() {
        return VALUES;
    }

    private final String name;
    private final String userIdColumn = COLUMN_USER_ID;
    private final String clientIdColumn = COLUMN_CLIENT_ID;
    private final String yclidColumn = COLUMN_YCLID;
    private final List<String> commonColumns = of(COLUMN_DATE_TIME, COLUMN_PRICE, COLUMN_CURRENCY);
    private final List<String> additionalColumns;
    private final String uploadPath;
    private final String findByIdPath;
    private final String findAllPath;
    private final String extendedThresholdPath;
    private final Class<T> dataClass;
    private final Supplier<T> dataSupplier;

    OfflineConversionType(
            String name,
            List<String> additionalColumns,
            String uploadPath,
            String findByIdPath,
            String findAllPath,
            String extendedThresholdPath,
            Class<T> dataClass,
            Supplier<T> dataSupplier
    ) {
        this.name = name;
        this.additionalColumns = additionalColumns;
        this.uploadPath = uploadPath;
        this.findByIdPath = findByIdPath;
        this.findAllPath = findAllPath;
        this.extendedThresholdPath = extendedThresholdPath;
        this.dataClass = dataClass;
        this.dataSupplier = dataSupplier;
    }

    @Override
    public String toString() {
        return name;
    }

    public List<String> getCommonColumns(OfflineConversionUploadingClientIdType clientIdType) {
        ImmutableList.Builder<String> builder = ImmutableList.builder();
        switch (clientIdType) {
            case USER_ID:
                builder.add(userIdColumn);
                break;
            case CLIENT_ID:
                builder.add(clientIdColumn);
                break;
            case YCLID:
                builder.add(yclidColumn);
                break;
        }
        return builder
                .addAll(commonColumns)
                .build();
    }

    public List<String> getColumns(OfflineConversionUploadingClientIdType clientIdType) {
        return ImmutableList.<String>builder()
                .addAll(getCommonColumns(clientIdType))
                .addAll(additionalColumns)
                .build();
    }

    public String getName() {
        return name;
    }

    public String getUserIdColumn() {
        return userIdColumn;
    }

    public String getClientIdColumn() {
        return clientIdColumn;
    }

    public String getYclidColumn() {
        return yclidColumn;
    }

    public List<String> getAdditionalColumns() {
        return additionalColumns;
    }

    public String getUploadPath() {
        return uploadPath;
    }

    public String getFindByIdPath() {
        return findByIdPath;
    }

    public String getFindAllPath() {
        return findAllPath;
    }

    public String getExtendedThresholdPath() {
        return extendedThresholdPath;
    }

    public Class<T> getDataClass() {
        return dataClass;
    }

    public T createData() {
        return dataSupplier.get();
    }
}
