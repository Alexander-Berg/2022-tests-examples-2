package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.List;
import java.util.concurrent.TimeUnit;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.CloudExportRequestParams;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudExport;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportAdapter;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportStatus;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.awaitility.Awaitility.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_DEFAULT_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_DEFAULT_CLUSTER_NAME;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_VALID_SERVICE_ACCOUNT;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.steps.CloudExportsSteps.toAdapter;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCloudExport;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.editorCloudAuthKey;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.mobmet.cloud.model.CloudExportType.CONTINUOUS;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudExports.MANAGEMENT
})
@Title("Управление экспортом в облако")
public class CloudExportTest {

    private static final User USER = Users.SIMPLE_USER;
    private static final User SUPPORT = Users.SUPER_LIMITED;

    private static UserSteps userSteps = UserSteps.onTesting(USER);
    private static UserSteps supportSteps = UserSteps.onTesting(SUPPORT);

    private static long appId;
    private static CloudAuthKey addedCloudAuthKey;
    private static CloudExportAdapter expectedCloudExport;

    @BeforeClass
    public static void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedCloudAuthKey = userSteps.onCloudAuthKeysSteps().createCloudAuthKey(appId, editorCloudAuthKey());
    }

    @Before
    public void setUp() {
        assumeThat("Ключ сервисного аккаунта добавлен", addedCloudAuthKey, notNullValue());
        CloudExport export = defaultCloudExport()
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                .withClusterId(CLOUD_DEFAULT_CLUSTER)
                .withType(CONTINUOUS);

        expectedCloudExport = toAdapter(
                userSteps.onCloudExportsSteps().createCloudExport(appId, export)
                        // В этом тесте проверяем только management часть с сохранением в pg. Получится или нет
                        // создать таблицу
                        // в облаке не проверяем
                        .withStatus(null)
        ).withClusterName(CLOUD_DEFAULT_CLUSTER_NAME);
    }

    @Test
    public void testGetByAppId() {
        List<CloudExportAdapter> exports = userSteps.onCloudExportsSteps()
                .getCloudExportsList(appId, new CloudExportRequestParams())
                .getExports();

        boolean containsExpected = exports.stream()
                .anyMatch(export -> export.getId().equals(expectedCloudExport.getId()));

        assertThat("список экспортов приложения содержит ожидаемый", containsExpected, equalTo(true));
    }

    @Test
    public void testGetById() {
        given().ignoreExceptions()
                .await()
                .atMost(30, TimeUnit.SECONDS)
                .pollInterval(1, TimeUnit.SECONDS)
                .until(
                        () -> userSteps.onCloudExportsSteps().getCloudExport(appId, expectedCloudExport.getId()),
                        equivalentTo(expectedCloudExport)
                );
    }

    @Test
    public void testGetByAppIdWithCustomRequestParams() throws InterruptedException {
        CloudExportRequestParams requestParams = new CloudExportRequestParams()
                .withLimit(1)
                .withOffset(1)
                .withSort("create_time")
                .withSortOrder("desc");

        CloudExport oneMoreExport = defaultCloudExport()
                .withServiceAccountId(CLOUD_VALID_SERVICE_ACCOUNT)
                .withClusterId(CLOUD_DEFAULT_CLUSTER)
                .withType(CONTINUOUS);

        try {
            Thread.sleep(1000);
            oneMoreExport = userSteps.onCloudExportsSteps().createCloudExport(appId, oneMoreExport);
            ManagementV1ApplicationAppIdExportCloudGETSchema actualCloudExports =
                    userSteps.onCloudExportsSteps().getCloudExportsList(appId, requestParams);

            assumeThat("список экспортов непустой", actualCloudExports.getExports().size(), equalTo(1));
            assumeThat("список экспортов непустой", actualCloudExports.getTotals(), greaterThanOrEqualTo(2L));

            CloudExportAdapter actual = actualCloudExports.getExports().get(0);
            assertThat("полученный экспорт эквивалентен добавленному", actual.getId(),
                    equivalentTo(expectedCloudExport.getId()));
        } finally {
            if (oneMoreExport != null) {
                supportSteps.onCloudExportsSteps().deleteCloudExport(appId, oneMoreExport.getId());
            }
        }
    }

    @Test
    public void testStop() {
        userSteps.onCloudExportsSteps().stopCloudExport(appId, expectedCloudExport.getId());

        CloudExportAdapter actual = userSteps.onCloudExportsSteps()
                .getCloudExport(appId, expectedCloudExport.getId());

        assertThat("экспорт остановлен", actual.getStatus(), equivalentTo(CloudExportStatus.STOPPED));
    }

    @Test
    public void testDelete() {
        supportSteps.onCloudExportsSteps().deleteCloudExport(appId, expectedCloudExport.getId());

        List<CloudExportAdapter> exports = userSteps.onCloudExportsSteps()
                .getCloudExportsList(appId, new CloudExportRequestParams())
                .getExports();
        boolean containsExpected = exports.stream()
                .anyMatch(export -> export.getId().equals(expectedCloudExport.getId()));
        assertThat("список экспортов не содержит удалённый", containsExpected, equalTo(false));
    }

    @After
    public void tearDown() {
        if (expectedCloudExport != null) {
            supportSteps.onCloudExportsSteps().deleteCloudExport(appId, expectedCloudExport.getId());
        }
    }

    @AfterClass
    public static void teardown() {
        if (addedCloudAuthKey != null) {
            userSteps.onCloudAuthKeysSteps().deleteCloudAuthKey(appId, addedCloudAuthKey.getId());
        }
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
