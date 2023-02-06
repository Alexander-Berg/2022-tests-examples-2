package ru.yandex.metrika.mobmet.crash.decoder.steps;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;

import static java.math.BigInteger.valueOf;
import static ru.yandex.metrika.mobmet.crash.decoder.steps.CrashDataParams.commonCrashParams;
import static ru.yandex.metrika.mobmet.crash.decoder.steps.CrashDataParams.iosErrorParams;
import static ru.yandex.metrika.mobmet.crash.decoder.steps.CrashDataParams.libraryCrashParams;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ANR;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_CRASH;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ERROR;

public class CrashTestDataReader {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static CrashTestData readCrashForDecode(long eventId) {
        return readCrash(commonCrashParams(eventId, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_2"));
    }

    /**
     * EventID нужно менять осторожно, потому что у библиотечных крешей он фигурирует в тестовых json файлах
     * и на его основе генерируется EventNumber, который учавствует в рассчёте EventID для креша бибиотеки.
     * {@link MobmetCrashDecoderSteps#fillCrashFields}
     * Предлагается для новых iOS крешей продолжать нумерацию с 1000, а для Android как есть сейчас.
     * Ну или придумать что-то получше.
     */
    public static final List<CrashDataParams> CRASH_DATA_PARAMS = ImmutableList.<CrashDataParams>builder()
            .add(commonCrashParams(1, 25378, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/music"))
            // EventID=10977833192963940072, AppVersionName=462, AppBuildNumber=28518
            .add(libraryCrashParams(2, 25378, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/music_sdk_crash", "sdk_processing_fields.json"))
            .add(commonCrashParams(3, 18895, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/disk"))
            .add(commonCrashParams(4, 10180, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/translate"))
            // EventID=599976850597222651, AppVersionName=5.3.0, AppBuildNumber=11896
            .add(commonCrashParams(5, 10267, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/kinopoisk"))
            // номер здесь, это номер креша в списке крешей приложения MetricaSample
            .add(commonCrashParams(6, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_2"))
            .add(commonCrashParams(7, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_11"))
            .add(commonCrashParams(8, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_18"))
            // EventID=6707652655769164054
            .add(commonCrashParams(9, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_19"))
            // https://fabric.io/yandexappmetrica/ios/apps/ru.yandex.mobile.metricasample/issues/5cbd82bdf8b88c2963e146ee/sessions/01dd9ca69b2a41a395dd2d842baf163b_DNE_0_v2?build=104263702
            .add(commonCrashParams(10, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_28"))
            // https://fabric.io/yandexappmetrica/ios/apps/ru.yandex.mobile.metricasample/issues/5c6abbfff8b88c296345da4c/sessions/046d599c2bb041fdb1b4307ad90f6a33_DNE_0_v2?build=104263702
            .add(commonCrashParams(11, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_29"))
            // EventId=13546240607251881992,osVersion=9.3.3,AppBuildNumber=15098,AppVersionName=370, символы не нужны
            .add(commonCrashParams(12, 28620, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/crash_without_symbols"))
            // EventID=480635182780693881, AppBuildNumber=15214
            .add(iosErrorParams(13, 28620, "ios", EVENT_PROTOBUF_ERROR, "EXCEPTION 1", "crashes/ios/error_with_stacktrace"))
            // EventID=9575033834922661605
            .add(iosErrorParams(14, 25378, "ios", EVENT_PROTOBUF_ERROR,
                    "com.edadeal.favoriteDataSyncService code: 1: Incident Identifier: 50719901-0477-41A6-AD46-B2C2CC2DBB8D",
                    "crashes/ios/error_without_stacktrace"))
            // EventId=753311128739803971, AppBuildNumber=15214
            .add(commonCrashParams(15, 28620, "ios", EVENT_PROTOBUF_ANR, "crashes/ios/anr"))
            // EventId=9268512962127215435, AppBuildNumber=18177, AppVersionName=282, OSVersion=12.4
            .add(commonCrashParams(16, 18895, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/MOBMET-10925"))
            // EventId=8676550836840109615, нет символов приложения и частично системных
            .add(commonCrashParams(17, 38000, "ios", EVENT_PROTOBUF_CRASH, "crashes/ios/MOBMET-11191"))
            // EventId=15580117785213006596, брал из инвалидов. AppBuildNumber=16863
            .add(iosErrorParams(1018, 28620, "ios", EVENT_PROTOBUF_ERROR, "", "crashes/ios/error_custom"))
            // EventId=6726739726945561519, брал из инвалидов. AppBuildNumber=17201
            .add(iosErrorParams(1019, 28620, "ios", EVENT_PROTOBUF_ERROR, "", "crashes/ios/error_nserror"))
            // EventId=8083515740917998808, брал из инвалидов. AppBuildNumber=17201.
            // Должен быть полезен, когда мы захотим деманглить классы с ошибкой
            .add(iosErrorParams(1020, 28620, "ios", EVENT_PROTOBUF_ERROR, "", "crashes/ios/error_custom_mangled"))
            // EventId=1033817182897459234
            .add(iosErrorParams(1021, 3049552, "ios", EVENT_PROTOBUF_ERROR, "", "crashes/ios/MOBMET-14039"))
            // iOS Flutter
            .add(commonCrashParams(1200, 7633, "ios", EVENT_PROTOBUF_CRASH, "crashes/flutter/ios_flutter-crash-11923795939279766376"))
            .add(commonCrashParams(1201, 7633, "ios", EVENT_PROTOBUF_ERROR, "crashes/flutter/ios_flutter-error-7024917473067146049"))
            .add(commonCrashParams(1202, 7633, "ios", EVENT_PROTOBUF_ERROR, "crashes/flutter/ios_flutter-custom_error-16991900502358374989"))
            // при добавлении нового теста прочитайте комментарий в начале

            // Android
            .add(commonCrashParams(18, 28620, "android", EVENT_PROTOBUF_CRASH, "crashes/proguard/crash_without_symbols"))
            .add(commonCrashParams(19, 28620, "android", EVENT_PROTOBUF_CRASH, "crashes/proguard/crash_with_symbols"))
            .add(libraryCrashParams(20, 28620, "android", EVENT_PROTOBUF_CRASH, "crashes/proguard/crash_with_lib_frame", "sdk_processing_fields.json"))
            .add(iosErrorParams(21, 28620, "android", EVENT_PROTOBUF_ERROR, "Случилось что-то нехорошее", "crashes/proguard/error_without_throwable"))
            .add(commonCrashParams(22, 28620, "android", EVENT_PROTOBUF_CRASH, "crashes/proguard/crash_without_throwable"))
            .add(commonCrashParams(23, 28620, "android", EVENT_PROTOBUF_ANR, "crashes/proguard/anr_without_throwable"))
            // EventID=8221973404796839265, AppVersionName=1.9.6, AppBuildNumber=87092
            .add(commonCrashParams(24, 917433, "android", EVENT_PROTOBUF_CRASH, "crashes/proguard/crash_with_symbols_compressed"))
            .add(commonCrashParams(25, 28620, "android", EVENT_PROTOBUF_ERROR, "crashes/proguard/error_without_affected_thread"))
            // Android r8
            .add(commonCrashParams(100, 28620, "android", EVENT_PROTOBUF_CRASH, "crashes/r8/crash_with_symbols"))
            .add(commonCrashParams(101, 28620, "android", EVENT_PROTOBUF_CRASH, "crashes/r8/MOBMET-13245-lost-rows"))
            // Android flutter
            .add(commonCrashParams(200, 7633, "android", EVENT_PROTOBUF_CRASH, "crashes/flutter/android_flutter-crash-10028777523086836113"))
            .add(commonCrashParams(201, 7633, "android", EVENT_PROTOBUF_ERROR, "crashes/flutter/android_flutter-error-9441546643700524976"))
            // при добавлении нового теста прочитайте комментарий в начале

            .build();

    public static CrashTestData readCrash(CrashDataParams params) {
        List<CrashProcessingFields> expected = new ArrayList<>();
        CrashProcessingFields main = readProcessingData(params.crashFieldsPath(), "processing_fields.json");
        main.setApiKey(params.appId());
        main.setEventID(valueOf(params.eventId()));
        expected.add(main);
        if (params.libraryCrashFieldsPath() != null) {
            CrashProcessingFields library = readProcessingData(params.crashFieldsPath(), params.libraryCrashFieldsPath());
            expected.add(library);
        }
        byte[] eventValue = readEventValue(params.crashFieldsPath());
        CrashInputFields inputFields = new CrashInputFields(
                params.eventId(), params.appId(), params.os(), params.eventType(), params.eventName(),
                eventValue);
        return new CrashTestData(inputFields, expected);
    }

    private static byte[] readEventValue(String dataPath) {
        return getResourceBytes(resPath(dataPath, "event_value.bin"));
    }

    private static CrashProcessingFields readProcessingData(String dataPath, String processingFieldsFile) {
        try {
            String processingFields = getResourceString(resPath(dataPath, processingFieldsFile));
            CrashProcessingFields fields = new ObjectMapper().readValue(processingFields, CrashProcessingFields.class);
            String threadContent = StringUtils.stripEnd(getResourceString(resPath(dataPath, "crash_thread_content.txt")), "\n ");
            fields.setCrashThreadContent(threadContent);
            String crashDecodedEventValueBeautified = getResourceString(resPath(dataPath, "crash_decoded_event_value.json"));
            if (!crashDecodedEventValueBeautified.isEmpty()) {
                String crashDecodedEventValue = MAPPER.writeValueAsString(MAPPER.readTree(crashDecodedEventValueBeautified));
                fields.setCrashDecodedEventValue(crashDecodedEventValue);
            } else {
                fields.setCrashDecodedEventValue(crashDecodedEventValueBeautified);
            }
            return fields;
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    private static String resPath(String crashPath, String fileName) {
        return crashPath + "/" + fileName;
    }

    private static String getResourceString(String path) {
        return new String(getResourceBytes(path));
    }

    private static byte[] getResourceBytes(String path) {
        try {
            return Files.readAllBytes(Paths.get(path));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

}
