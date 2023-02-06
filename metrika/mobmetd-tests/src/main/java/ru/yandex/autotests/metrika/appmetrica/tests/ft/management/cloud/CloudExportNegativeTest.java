package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.time.LocalDate;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudExport;
import ru.yandex.metrika.mobmet.cloud.model.CloudTableType;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.time.format.DateTimeFormatter.ISO_LOCAL_DATE;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_DEFAULT_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_REPLICATED_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_STOPPED_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_WITHOUT_METRIKA_ACCESS;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_WITHOUT_ZK_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_DISABLED_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_EXPORT_INVALID_START_DATE;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ILLEGAL_EXPORT_FIELD;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_TABLE_ALREADY_EXISTS;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCloudExport;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.editorCloudAuthKey;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudExports.MANAGEMENT
})
@Title("Управление экспортом в облако (негативный)")
public class CloudExportNegativeTest {

    private static final User USER = Users.SIMPLE_USER;

    private static UserSteps userSteps = UserSteps.onTesting(USER);

    private static long appId;
    private static CloudAuthKey addedCloudAuthKey;

    @BeforeClass
    public static void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedCloudAuthKey = userSteps.onCloudAuthKeysSteps().createCloudAuthKey(appId, editorCloudAuthKey());
    }

    @Before
    public void assumeInit() {
        assumeThat("Ключ сервисного аккаунта добавлен", addedCloudAuthKey, notNullValue());
    }

    @Test
    public void illegalField() {
        CloudExport export = defaultCloudExport()
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                .withClusterId(CLOUD_DEFAULT_CLUSTER)
                .withFields(asList("application_id", "unexpected_field"));

        userSteps.onCloudExportsSteps().createCloudExportAndExpectError(appId, export, CLOUD_ILLEGAL_EXPORT_FIELD);
    }

    @Test
    public void clusterWithoutZK() {
        CloudExport export = defaultCloudExport()
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                .withClusterId(CLOUD_WITHOUT_ZK_CLUSTER);

        userSteps.onCloudExportsSteps().createCloudExportAndExpectError(appId, export, CLOUD_DISABLED_CLUSTER);
    }

    @Test
    public void clusterWithoutMetrikaAccess() {
        CloudExport export = defaultCloudExport()
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                .withClusterId(CLOUD_WITHOUT_METRIKA_ACCESS);

        userSteps.onCloudExportsSteps().createCloudExportAndExpectError(appId, export, CLOUD_DISABLED_CLUSTER);
    }

    @Test
    public void oldStartDate() {
        CloudExport export = defaultCloudExport()
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                .withClusterId(CLOUD_DEFAULT_CLUSTER)
                .withFromDate(LocalDate.now().minusDays(1).format(ISO_LOCAL_DATE));

        userSteps.onCloudExportsSteps().createCloudExportAndExpectError(appId, export, CLOUD_EXPORT_INVALID_START_DATE);
    }

    @Test
    public void tableAlreadyExistsForNewTableType() {
        CloudExport export = defaultCloudExport()
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                .withClusterId(CLOUD_REPLICATED_SHARD_CLUSTER)
                .withClickhouseTableName(TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA)
                .withTableType(CloudTableType.NEW);

        userSteps.onCloudExportsSteps().createCloudExportAndExpectError(appId, export, CLOUD_TABLE_ALREADY_EXISTS);
    }

    @Test
    public void stoppedCluster() {
        CloudExport export = defaultCloudExport()
                .withClusterId(CLOUD_STOPPED_CLUSTER);

        userSteps.onCloudExportsSteps().createCloudExportAndExpectError(appId, export, CLOUD_DISABLED_CLUSTER);
    }

    @AfterClass
    public static void teardown() {
        if (addedCloudAuthKey != null) {
            userSteps.onCloudAuthKeysSteps().deleteCloudAuthKey(appId, addedCloudAuthKey.getId());
        }
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
