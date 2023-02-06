package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.List;

import org.hamcrest.Matchers;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.steps.CloudExportMetaSteps;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportFieldMeta;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_REPLICATED_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_VALID_SERVICE_ACCOUNT;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudExports.GET_META
})
@Title("Получение меты для экспорта в облако")
public class CloudExportMetaTest {

    private static final CloudExportFieldMeta ONE_OF_EXPECTED_FIELDS = new CloudExportFieldMeta()
            .withTableName("client_events")
            .withFieldName("ios_ifa")
            .withClickhouseOutName("ios_ifa")
            .withClickhouseType("String")
            .withOrderNumber(200L)
            .withRequired(false)
            .withPartitioningKey(false);

    private static final CloudExportMetaSteps cloudExportMetaSteps =
            UserSteps.onTesting(SUPER_LIMITED).onCloudExportMetaSteps();

    @Test
    public void testGetFields() {
        List<CloudExportFieldMeta> cloudExportFields = cloudExportMetaSteps.getCloudExportFields();
        assumeThat("список полей непустой", cloudExportFields, not(empty()));

        assertThat("содержит ожидаемое поле", cloudExportFields, Matchers.hasItem(ONE_OF_EXPECTED_FIELDS));
    }

    @Test
    public void testGetTables() {
        cloudExportMetaSteps.getTables(PUSH_SAMPLE.get(ID),
                CLOUD_VALID_SERVICE_ACCOUNT, CLOUD_REPLICATED_SHARD_CLUSTER);
    }
}
