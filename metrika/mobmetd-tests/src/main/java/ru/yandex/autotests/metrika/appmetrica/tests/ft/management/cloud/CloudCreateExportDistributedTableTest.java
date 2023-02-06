package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.List;
import java.util.concurrent.TimeUnit;

import com.google.common.collect.ImmutableList;
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
import ru.yandex.metrika.mobmet.cloud.model.CloudExportDetails;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.awaitility.Awaitility.given;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_REPLICATED_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.steps.CloudExportsSteps.toAdapter;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCloudExport;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudExports.MANAGEMENT
})
@Title("Создание в облаке таблиц для экспортов (distributed)")
@RunWith(Parameterized.class)
public class CloudCreateExportDistributedTableTest {

    private static final long APP_ID = PUSH_SAMPLE.get(ID);

    private static final String REPLICATED_TABLE_PATTERN = "" +
            "CREATE TABLE appmetrica_exports.%s\n" +
            "(\n    `application_id` UInt32,\n    `ios_ifa` String,\n    `ios_ifv` String,\n    `android_id` String," +
            "\n    `google_aid` String,\n    `os_name` String,\n    `os_version` String," +
            "\n    `device_manufacturer` String,\n    `device_model` String,\n    `device_type` String," +
            "\n    `device_locale` String,\n    `app_version_name` String,\n    `app_package_name` String," +
            "\n    `event_name` String,\n    `event_json` String,\n    `event_date` Date," +
            "\n    `event_datetime` DateTime,\n    `event_timestamp` UInt64,\n    `event_receive_datetime` DateTime," +
            "\n    `event_receive_timestamp` UInt64,\n    `connection_type` String,\n    `operator_name` String," +
            "\n    `mcc` UInt32,\n    `mnc` UInt32,\n    `country_iso_code` String,\n    `city` String," +
            "\n    `appmetrica_device_id` UInt64\n)\n" +
            "ENGINE = ReplicatedMergeTree(" +
            "'/clickhouse-appmetrica_exports/tables/{shard}/%s', " +
            "'{replica}')\n" +
            "PARTITION BY toMonday(event_date)\n" +
            "ORDER BY (application_id, event_date, appmetrica_device_id)\n" +
            "SAMPLE BY appmetrica_device_id\nSETTINGS index_granularity = 8192";

    private static final String DISTRIBUTED_SHARDED_TABLE_PATTERN = "" +
            "CREATE TABLE appmetrica_exports.%s_distributed\n" +
            "(\n    `application_id` UInt32,\n    `ios_ifa` String,\n    `ios_ifv` String,\n    `android_id` String," +
            "\n    `google_aid` String,\n    `os_name` String,\n    `os_version` String,\n    `device_manufacturer` " +
            "String," +
            "\n    `device_model` String,\n    `device_type` String,\n    `device_locale` String," +
            "\n    `app_version_name` String,\n    `app_package_name` String,\n    `event_name` String," +
            "\n    `event_json` String,\n    `event_date` Date,\n    `event_datetime` DateTime," +
            "\n    `event_timestamp` UInt64,\n    `event_receive_datetime` DateTime,\n    `event_receive_timestamp` " +
            "UInt64," +
            "\n    `connection_type` String,\n    `operator_name` String,\n    `mcc` UInt32,\n    `mnc` UInt32," +
            "\n    `country_iso_code` String,\n    `city` String,\n    `appmetrica_device_id` UInt64\n)\n" +
            "ENGINE = Distributed(" +
            "'{cluster}', 'appmetrica_exports', '%s', appmetrica_device_id)";

    private static final User USER = Users.SUPER_LIMITED;

    private static UserSteps userSteps = UserSteps.onTesting(USER);

    @Parameter
    public String description;

    @Parameter(1)
    public String clusterId;

    private CloudExportAdapter addedCloudExport;

    @Parameterized.Parameters(name = "{0}")
    public static List<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(params("cluster with replication", CLOUD_REPLICATED_SHARD_CLUSTER))
                // TODO: Restore CLOUD_ONE_NODE_SHARD_CLUSTER
                // .add(params("cluster with zk and with one node shard", CLOUD_ONE_NODE_SHARD_CLUSTER))
                .build();
    }

    private static Object[] params(String description, String clusterId) {
        return new Object[]{description, clusterId};
    }

    @Before
    public void setup() {
        CloudExport export = defaultCloudExport()
                .withClusterId(clusterId);

        addedCloudExport = toAdapter(userSteps.onCloudExportsSteps().createCloudExport(APP_ID, export));
    }

    @Test
    public void checkExportTableSql() {
        given().ignoreExceptions()
                .await()
                .atMost(180, TimeUnit.SECONDS)
                .pollDelay(5, TimeUnit.SECONDS)
                .pollInterval(5, TimeUnit.SECONDS)
                .until(
                        () -> userSteps.onCloudExportsSteps()
                                .showCloudExportCreateTableSql(APP_ID, addedCloudExport.getId()),
                        allOf(
                                having(on(CloudExportDetails.class).getCreateTableSql(),
                                        equalTo(String.format(REPLICATED_TABLE_PATTERN,
                                                addedCloudExport.getClickhouseTableName(),
                                                addedCloudExport.getClickhouseTableName()))),
                                having(on(CloudExportDetails.class).getCreateDistributedTableSql(),
                                        equalTo(String.format(DISTRIBUTED_SHARDED_TABLE_PATTERN,
                                                addedCloudExport.getClickhouseTableName(),
                                                addedCloudExport.getClickhouseTableName())))
                        ));
    }

    @After
    public void teardown() {
        if (addedCloudExport != null) {
            userSteps.onCloudExportsSteps().stopCloudExport(APP_ID, addedCloudExport.getId());
            userSteps.onCloudExportsSteps().dropExportTableAndIgnoreResult(APP_ID, addedCloudExport);
            userSteps.onCloudExportsSteps().deleteCloudExport(APP_ID, addedCloudExport.getId());
        }
    }
}
