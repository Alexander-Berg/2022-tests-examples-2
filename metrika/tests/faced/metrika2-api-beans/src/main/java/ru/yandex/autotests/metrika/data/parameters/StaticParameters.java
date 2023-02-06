package ru.yandex.autotests.metrika.data.parameters;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Вспомогательный хелпер, содержит статические фабричные функции для некоторых,
 * используемых в тестах параметров запросов
 * <p>
 * Created by konkov on 12.07.2016.
 */
public final class StaticParameters {
    private StaticParameters() {}

    public static IFormParameters requestDomain(String requestDomain) {
        return new CommonParameters().withRequestDomain(requestDomain);
    }

    public static IFormParameters lang(String lang) {
        return new CommonReportParameters().withLang(lang);
    }

    public static IFormParameters limit(Long limit) {
        return new CommonReportParameters().withLimit(limit);
    }

    public static IFormParameters offset(Long offset) {
        return new CommonReportParameters().withOffset(offset);
    }

    public static IFormParameters uid(Long uid) { return new CommonParameters().withUid(uid); }

    public static IFormParameters ignoreQuota(boolean value) {
        return makeParameters("quota_ignore", value);
    }

    public static IFormParameters timezone(String timezone) {
        return makeParameters("timezone", timezone);
    }

}
