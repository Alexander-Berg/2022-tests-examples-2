package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.Collection;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudExport;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportAdapter;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportStatus;
import ru.yandex.metrika.mobmet.cloud.model.CloudTableType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_DEFAULT_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_REPLICATED_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA;
import static ru.yandex.autotests.metrika.appmetrica.steps.CloudExportsSteps.toAdapter;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCloudExport;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudExports.MANAGEMENT
})
@Title("Возобновление сломанного экспорта в облако")
@RunWith(Parameterized.class)
public class CloudExportResumeTest {

    private static final long APP_ID = PUSH_SAMPLE.get(ID);

    private static final User USER = Users.SUPER_LIMITED;

    private static final UserSteps userSteps = UserSteps.onTesting(USER);

    @Parameter
    public String description;

    @Parameter(1)
    public CloudExport export;

    @Parameter(2)
    public CloudExportStatus expectedResumedStatus;

    public CloudExportAdapter addedCloudExport;

    @Parameterized.Parameters(name = "{0}. Expected resumed export status {2}")
    public static Collection<Object[]> parameters() {
        return asList(
                params("Resume export with new table",
                        defaultCloudExport()
                                .withClusterId(CLOUD_DEFAULT_CLUSTER),
                        CloudExportStatus.RESUMED),
                params("Resume export with existing table",
                        defaultCloudExport()
                                .withClusterId(CLOUD_REPLICATED_SHARD_CLUSTER)
                                .withTableType(CloudTableType.EXISTING)
                                .withClickhouseTableName(TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA)
                                .withFields(asList("event_name", "event_timestamp", "event_receive_datetime")),
                        CloudExportStatus.READY_FOR_EXPORT));
    }

    private static Object[] params(String description, CloudExport export, CloudExportStatus expectedStatus) {
        return new Object[]{description, export, expectedStatus};
    }

    @Before
    public void setup() {
        addedCloudExport = toAdapter(userSteps.onCloudExportsSteps().createCloudExport(APP_ID, export));
    }

    @Test
    public void testResumeStoppedExportWithNewTable() {
        userSteps.onCloudExportsSteps().stopCloudExport(APP_ID, addedCloudExport.getId());
        userSteps.onCloudExportsSteps().resumeCloudExport(APP_ID, addedCloudExport.getId());

        CloudExportAdapter cloudExport = userSteps.onCloudExportsSteps().getCloudExport(APP_ID,
                addedCloudExport.getId());
        assertThat(cloudExport.getStatus(), equalTo(expectedResumedStatus));
    }

    @After
    public void teardown() {
        if (addedCloudExport != null) {
            if (!addedCloudExport.getClickhouseTableName().equals(TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA)) {
                userSteps.onCloudExportsSteps().dropExportTableAndIgnoreResult(APP_ID, addedCloudExport);
            }
            userSteps.onCloudExportsSteps().deleteCloudExport(APP_ID, addedCloudExport.getId());
        }
    }
}
