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
import java.util.List;
import java.util.stream.IntStream;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.SYMBOLS_UPLOAD_QUOTA_EXCEEDED;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.CrashCreator.loadSymbolsFileContent;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.PROGUARD_MAPPING_UPLOAD
})
@Title("Превышение квоты на загрузку файлов символов")
@RunWith(Parameterized.class)
public class UploadSymbolsQuotaTest {

    // Для теста на виртуалках и в тестинге установлена квота 2 загрузки в 30 секунд.
    private static final int MAX_UPLOADS_COUNT = 2;

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    @Parameter
    public String testDescription;

    @Parameter(1)
    public boolean uploadByAppId;

    private Application addedApplication;

    private List<SymbolsUploadMeta> uploadedSymbols;

    private byte[] uploadProguardMappingContent;

    @Parameters(name = "Upload by {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                params("appId", true),
                params("post_api_key", false)
        );
    }

    public static Object[] params(String description, boolean isUploadByAppId) {
        return new Object[]{description, isUploadByAppId};
    }

    @Before
    public void setup() {
        uploadProguardMappingContent = loadSymbolsFileContent("mapping.zip");

        addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());

        uploadedSymbols = IntStream.range(0, MAX_UPLOADS_COUNT)
                .mapToObj(this::uploadSymbols)
                .collect(toList());
    }

    @Test
    public void testQuotaExceed() {
        uploadSymbolsAndExpectError();
    }

    @After
    public void teardown() {
        for (SymbolsUploadMeta meta : uploadedSymbols) {
            userSteps.onCommonSymbolsUploadSteps().deleteSymbolsIgnoringResult(meta.getAppId(), meta.getId());
        }
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(addedApplication.getId());
    }

    private SymbolsUploadMeta uploadSymbols(int i) {
        long appId = addedApplication.getId();
        String postApiKey = addedApplication.getImportToken();

        if (uploadByAppId) {
            return userSteps.onCommonSymbolsUploadSteps().uploadSymbols(appId, SymbolsTypeParam.proguard, uploadProguardMappingContent);
        } else {
            return userSteps.onCommonSymbolsUploadSteps().uploadSymbols(postApiKey, SymbolsTypeParam.proguard, uploadProguardMappingContent);
        }
    }

    private void uploadSymbolsAndExpectError() {
        if (uploadByAppId) {
            userSteps.onCommonSymbolsUploadSteps().uploadSymbolsAndExpectError(addedApplication.getId(),
                    SymbolsTypeParam.proguard, uploadProguardMappingContent, SYMBOLS_UPLOAD_QUOTA_EXCEEDED);
        } else {
            userSteps.onCommonSymbolsUploadSteps().uploadSymbolsAndExpectError(addedApplication.getImportToken(),
                    SymbolsTypeParam.proguard, uploadProguardMappingContent, SYMBOLS_UPLOAD_QUOTA_EXCEEDED);
        }
    }
}
