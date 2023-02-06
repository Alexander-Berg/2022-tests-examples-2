package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.List;

import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudCluster;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasItems;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_DEFAULT_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_REPLICATED_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_STOPPED_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_VALID_SERVICE_ACCOUNT;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_WITHOUT_METRIKA_ACCESS;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_WITHOUT_ZK_CLUSTER;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudClusters.GET_LIST
})
@Title("Получение списка кластеров")
public class CloudClustersTest {

    private static final User USER = Users.SUPER_LIMITED;
    private static UserSteps userSteps = UserSteps.onTesting(USER);

    private final CloudCluster[] expectedClusters = new CloudCluster[]{
            new CloudCluster()
                    .withId(CLOUD_STOPPED_CLUSTER)
                    .withName("cloud-export-stopped")
                    .withEnabled(false),
            new CloudCluster()
                    .withId(CLOUD_DEFAULT_CLUSTER)
                    .withName("cloud-export-default")
                    .withEnabled(true),
            new CloudCluster()
                    .withId(CLOUD_WITHOUT_ZK_CLUSTER)
                    .withName("cloud-export-without-zk")
                    .withEnabled(false),
            new CloudCluster()
                    .withId(CLOUD_WITHOUT_METRIKA_ACCESS)
                    .withName("cloud-export-without-metrika-access")
                    .withEnabled(false),
            /* TODO: Restore CLOUD_ONE_NODE_SHARD_CLUSTER
            new CloudCluster()
                    .withId(CLOUD_ONE_NODE_SHARD_CLUSTER)
                    .withName("cloud-export-one-node-shard")
                    .withEnabled(true),*/
            new CloudCluster()
                    .withId(CLOUD_REPLICATED_SHARD_CLUSTER)
                    .withName("cloud-export-replicated-shard")
                    .withEnabled(true)};

    @Test
    public void testGetClusters() {
        List<CloudCluster> actualClusters = userSteps.onCloudClustersSteps().getCloudClusters(
                PUSH_SAMPLE.get(ID), CLOUD_VALID_SERVICE_ACCOUNT);
        assertThat("Полученный список кластеров эквивалентен ожидаемому", actualClusters, hasItems(expectedClusters));
    }
}
