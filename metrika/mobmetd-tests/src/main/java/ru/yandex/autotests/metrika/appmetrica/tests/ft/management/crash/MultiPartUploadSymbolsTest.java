package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import com.google.common.primitives.Bytes;
import org.apache.commons.lang3.RandomUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.metrika.mobmet.crash.SymbolsUploadMeta;
import ru.yandex.metrika.mobmet.management.Application;

import java.util.concurrent.TimeUnit;

import static org.awaitility.Awaitility.given;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.crash.SymbolsTypeParam.proguard;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.CrashCreator.loadSymbolsFileContent;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

public class MultiPartUploadSymbolsTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SUPER_LIMITED);

    private long appId;

    private SymbolsUploadMeta actualUploadMeta;

    private byte[] symbolsContent;

    @Before
    public void setup() {
        byte[] realZip = loadSymbolsFileContent("mapping.zip");
        byte[] random15Mb = RandomUtils.nextBytes(15 * (int) Math.pow(2, 20));
        // Настоящий zip нам нужен для правильного zip-заголовка, чтобы файл прошёл валидацию
        symbolsContent = Bytes.concat(realZip, random15Mb);

        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        String postApiKey = addedApplication.getImportToken();
        actualUploadMeta = userSteps.onCommonSymbolsUploadSteps().uploadSymbols(postApiKey, proguard, symbolsContent);
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
}
