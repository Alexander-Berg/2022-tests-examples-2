package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.body.CustomEntityBody;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonHeaders;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.ReportGroup;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.SymbolsTypeParam;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.crash.SymbolsUploadMeta;
import ru.yandex.metrika.mobmet.crash.response.mappings.MappingsListing;
import ru.yandex.metrika.mobmet.crash.response.mappings.MissingMappingsStat;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static org.apache.http.HttpHeaders.CONTENT_TYPE;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.core.ClientUtils.APPLICATION_ZIP;
import static ru.yandex.autotests.metrika.appmetrica.core.ClientUtils.APPLICATION_ZIP_UTF_8;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;

public class CommonSymbolsUploadSteps extends AppMetricaBaseSteps {

    public CommonSymbolsUploadSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Загрузить файл символов {1} для {0}")
    @ParallelExecution(ALLOW)
    public SymbolsUploadMeta uploadSymbols(long appId, SymbolsTypeParam symbolsType, byte[] symbolsContent) {
        return doUploadSymbols(appId, symbolsType, symbolsContent, SUCCESS_MESSAGE, expectSuccess())
                .getSymbolsUploadMeta();
    }

    @Step("Загрузить файл символов {1} для {0}")
    @ParallelExecution(ALLOW)
    public SymbolsUploadMeta uploadSymbols(String postApiKey, SymbolsTypeParam symbolsType, byte[] symbolsContent) {
        return doUploadSymbols(postApiKey, symbolsType, symbolsContent, SUCCESS_MESSAGE, expectSuccess())
                .getSymbolsUploadMeta();
    }

    @Step("Загрузить файл символов {1} для {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public SymbolsUploadMeta uploadSymbolsAndExpectError(Long appId,
                                                         SymbolsTypeParam symbolsType,
                                                         byte[] symbolsContent,
                                                         IExpectedError error) {
        return doUploadSymbols(appId, symbolsType, symbolsContent, ERROR_MESSAGE, expectError(error))
                .getSymbolsUploadMeta();
    }

    @Step("Загрузить файл символов {1} для {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public SymbolsUploadMeta uploadSymbolsAndExpectError(String postApiKey,
                                                         SymbolsTypeParam symbolsType,
                                                         byte[] symbolsContent,
                                                         IExpectedError error) {
        return doUploadSymbols(postApiKey, symbolsType, symbolsContent, ERROR_MESSAGE, expectError(error))
                .getSymbolsUploadMeta();
    }

    @Step("Получить для приложения {0} файл символов {1}")
    @ParallelExecution(ALLOW)
    public CustomEntityBody getSymbolsFile(long appId, Long symbolsId) {
        return doGetSymbolsFile(appId, symbolsId);
    }

    @Step("Получить для приложения {0} список загруженных и недостающих {1} символов")
    @ParallelExecution(RESTRICT)
    public MappingsListing getSymbolsList(long appId, SymbolsTypeParam symbolsType) {
        return getSymbolsList(SUCCESS_MESSAGE, expectSuccess(), appId, symbolsType).getMappings();
    }

    @Step("({0}) Получить для приложения {1} информацию о недостающих {2} символах")
    @ParallelExecution(RESTRICT)
    public MissingMappingsStat getMissingSymbolsStat(ReportGroup report, long appId, SymbolsTypeParam symbolsType) {
        return getMissingSymbolsStat(SUCCESS_MESSAGE, expectSuccess(), appId, report, symbolsType, null).getResponse();
    }

    @Step("({0}) Получить для приложения {1} и крэш-группы {3} информацию о недостающих {2} символах")
    @ParallelExecution(RESTRICT)
    public MissingMappingsStat getMissingSymbolsStat(ReportGroup report, long appId, SymbolsTypeParam symbolsType, String crashGroupId) {
        return getMissingSymbolsStat(SUCCESS_MESSAGE, expectSuccess(), appId, report, symbolsType, crashGroupId).getResponse();
    }

    @Step("Удалить для приложения {0} файл символов {1}")
    @ParallelExecution(ALLOW)
    public void deleteSymbolsIgnoringResult(long appId, long symbolsId) {
        doDeleteSymbols(ANYTHING_MESSAGE, expectAnything(), appId, symbolsId);
    }

    private ManagementV1ApplicationAppIdCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeUploadPOSTSchema doUploadSymbols(
            long appId,
            SymbolsTypeParam symbolsTypeParam,
            byte[] content,
            String message,
            Matcher matcher
    ) {
        FreeFormParameters headers = makeParameters(CONTENT_TYPE, APPLICATION_ZIP_UTF_8);

        ManagementV1ApplicationAppIdCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeUploadPOSTSchema result = post(
                ManagementV1ApplicationAppIdCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeUploadPOSTSchema.class,
                format("/management/v1/application/%s/crash/%s/upload", appId, symbolsTypeParam.name()),
                headers,
                new CustomEntityBody(APPLICATION_ZIP, content)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeUploadPUTSchema doUploadSymbols(
            String postApiKey,
            SymbolsTypeParam symbolsType,
            byte[] content,
            String message,
            Matcher matcher
    ) {
        CommonHeaders headers = new CommonHeaders()
                .withPostApiKey(postApiKey)
                .withContentType(APPLICATION_ZIP_UTF_8);

        ManagementV1ApplicationCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeUploadPUTSchema result = put(
                ManagementV1ApplicationCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeUploadPUTSchema.class,
                format("/management/v1/application/crash/%s/upload", symbolsType),
                headers,
                new CustomEntityBody(APPLICATION_ZIP, content)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private CustomEntityBody doGetSymbolsFile(long appId, long symbolsId) {
        return get(CustomEntityBody.class,
                format("/internal/management/v1/application/%s/crash/symbols/%s", appId, symbolsId));
    }

    private InternalManagementV1ApplicationAppIdCrashSymbolsIdDELETESchema doDeleteSymbols(String message,
                                                                                           Matcher matcher,
                                                                                           long appId,
                                                                                           long symbolsId) {
        InternalManagementV1ApplicationAppIdCrashSymbolsIdDELETESchema result = delete(
                InternalManagementV1ApplicationAppIdCrashSymbolsIdDELETESchema.class,
                format("/internal/management/v1/application/%s/crash/symbols/%s", appId, symbolsId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeGETSchema getSymbolsList(
            String message,
            Matcher matcher,
            long appId,
            SymbolsTypeParam symbolsType
    ) {
        ManagementV1ApplicationAppIdCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeGETSchema result = get(
                ManagementV1ApplicationAppIdCrashSymbolsTypeAndroidIosProguardDsymAndroidNativeGETSchema.class,
                format("/management/v1/application/%s/crash/%s", appId, symbolsType));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdEventTypeCrashErrorAnrSymbolsTypeAndroidIosProguardDsymAndroidNativeMissingStatGETSchema getMissingSymbolsStat(
            String message,
            Matcher matcher,
            long appId,
            ReportGroup report,
            SymbolsTypeParam symbolsType,
            String crashGroupId
    ) {
        FreeFormParameters params = new FreeFormParameters();
        if (crashGroupId != null) {
            params.append("crash_group_id", crashGroupId);
        }
        ManagementV1ApplicationAppIdEventTypeCrashErrorAnrSymbolsTypeAndroidIosProguardDsymAndroidNativeMissingStatGETSchema result = get(
                ManagementV1ApplicationAppIdEventTypeCrashErrorAnrSymbolsTypeAndroidIosProguardDsymAndroidNativeMissingStatGETSchema.class,
                format("/management/v1/application/%s/%s/%s/missing/stat", appId, report, symbolsType),
                params);
        assertThat(message, result, matcher);
        return result;
    }
}
