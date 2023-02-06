package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.SymbolsTypeParam;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.crash.SymbolsUploadMeta;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.concurrent.TimeUnit;

import static org.awaitility.Awaitility.given;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.crash.SymbolsTypeParam.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.CrashCreator.loadSymbolsFileContent;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.ANDROID_NATIVE_SYMBOLS_UPLOAD,
        Requirements.Story.Crash.DSYM_UPLOAD,
        Requirements.Story.Crash.PROGUARD_MAPPING_UPLOAD,
})
@Title("Загрузка proguard mapping.txt для деобфускации андроидных крэшей")
@RunWith(Parameterized.class)
public class UploadSymbolsTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SUPER_LIMITED);

    @Parameter
    public String symbolsFilename;

    @Parameter(1)
    public SymbolsTypeParam symbolsType;

    @Parameter(2)
    public UploadType uploadType;

    private long appId;

    private SymbolsUploadMeta actualUploadMeta;

    private byte[] symbolsContent;

    @Parameters(name = "Upload {0} as {1} by {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                // Для фронтенда (типы символов по ОС)
                params("Haneke.framework.dSYM.zip", ios, UploadType.app_id),
                // Для плагинов сборки (конкретные типы символов)
                params("mapping.zip", proguard, UploadType.post_api_key),
                // Для плагинов сборки - unused (тиы символов по ОС)
                params("android_native.zip", android_native, UploadType.app_id)
        );
    }

    @Before
    public void setup() {
        symbolsContent = loadSymbolsFileContent(symbolsFilename);

        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        String postApiKey = addedApplication.getImportToken();

        switch (uploadType) {
            case app_id:
                actualUploadMeta = userSteps.onCommonSymbolsUploadSteps().uploadSymbols(appId, symbolsType, symbolsContent);
                break;
            case post_api_key:
                actualUploadMeta = userSteps.onCommonSymbolsUploadSteps().uploadSymbols(postApiKey, symbolsType, symbolsContent);
                break;
            default:
                throw new IllegalArgumentException("Unsupported upload type: " + uploadType);
        }
    }

    @Test
    public void uploadSymbolsFile() {
        assumeThat("Файл символов загружен", actualUploadMeta.getAppId(), equalTo(appId));

        given().ignoreExceptions()
                .await()
                .atMost(60, TimeUnit.SECONDS)
                .pollDelay(1, TimeUnit.SECONDS)
                .pollInterval(5, TimeUnit.SECONDS)
                .until(
                        () -> userSteps.onCommonSymbolsUploadSteps()
                                .getSymbolsFile(appId, actualUploadMeta.getId())
                                .getContent(),
                        equalTo(symbolsContent));
    }

    @After
    public void teardown() {
        userSteps.onCommonSymbolsUploadSteps().deleteSymbolsIgnoringResult(
                actualUploadMeta.getAppId(), actualUploadMeta.getId());
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] params(String filename, SymbolsTypeParam symbolsType, UploadType uploadType) {
        return new Object[]{filename, symbolsType, uploadType};
    }

    private enum UploadType {
        app_id,
        post_api_key
    }
}
