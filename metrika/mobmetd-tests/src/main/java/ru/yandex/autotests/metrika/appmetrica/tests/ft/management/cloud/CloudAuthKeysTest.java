package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthMaskedKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudCluster;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.RandomStringUtils.randomAlphanumeric;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ACCOUNT_DUPLICATED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_DENIED_VIEWER_ACCOUNT;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_INVALID_PRIVATE_KEY;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.editorCloudAuthKey;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.viewerCloudAuthKey;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudAuthKeys.EDIT
})
@Title("Редактирование данных о ключах для экспорта в облако")
public class CloudAuthKeysTest {

    private static final User USER = Users.SIMPLE_USER;
    private static UserSteps userSteps = UserSteps.onTesting(USER);

    private long appId;
    private CloudAuthKey addedCloudAuthKey;
    private CloudAuthMaskedKey addedCloudAuthMaskedKey;

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        addedCloudAuthKey = userSteps.onCloudAuthKeysSteps().createCloudAuthKey(appId, editorCloudAuthKey());
        addedCloudAuthMaskedKey = new CloudAuthMaskedKey()
                .withName(addedCloudAuthKey.getName())
                .withServiceAccountId(addedCloudAuthKey.getServiceAccountId());
    }

    @Test
    public void testGetByAppId() {
        List<CloudAuthMaskedKey> keys = userSteps.onCloudAuthKeysSteps().getCloudAuthKeysList(appId);

        assumeThat("список ключей содержит один ключ", keys.size(), equalTo(1));

        CloudAuthMaskedKey actual = keys.get(0);
        assertThat("полученный ключ эквивалентен добавленному", actual, equivalentTo(addedCloudAuthMaskedKey));
    }

    @Test
    public void testKey() {
        List<CloudCluster> clusters = userSteps.onCloudClustersSteps().getCloudClusters(
                appId, addedCloudAuthKey.getServiceAccountId());
        assertThat("с помощью добавленного ключа успешно выполняется запрос за кластерами", clusters, is(not(empty())));
    }

    @Test
    public void testDelete() {
        userSteps.onCloudAuthKeysSteps().deleteCloudAuthKey(appId, addedCloudAuthKey.getId());

        List<CloudAuthMaskedKey> keys = userSteps.onCloudAuthKeysSteps().getCloudAuthKeysList(appId);
        assertThat("список ключей пустой", keys, empty());
    }

    @Test
    public void testCreateInvalidServiceAccount() {
        userSteps.onCloudAuthKeysSteps().createCloudAuthKeyAndExpectError(
                appId,
                new CloudAuthKey()
                        .withName("Test key " + randomAlphanumeric(10))
                        .withFolderId(randomAlphanumeric(30))
                        .withServiceAccountId(randomAlphanumeric(100))
                        .withPublicKeyId(randomAlphanumeric(100))
                        .withPrivateKey(randomAlphanumeric(2000)),
                CLOUD_INVALID_PRIVATE_KEY);
    }

    @Test
    public void testCreateInvalidViewerServiceAccount() {
        userSteps.onCloudAuthKeysSteps().createCloudAuthKeyAndExpectError(
                appId,
                viewerCloudAuthKey(),
                CLOUD_DENIED_VIEWER_ACCOUNT);
    }

    @Test
    public void testCreateDuplicatedServiceAccount() {
        userSteps.onCloudAuthKeysSteps().createCloudAuthKeyAndExpectError(
                appId,
                new CloudAuthKey()
                        .withName("Test key " + randomAlphanumeric(10))
                        .withFolderId(addedCloudAuthKey.getFolderId())
                        .withServiceAccountId(addedCloudAuthKey.getServiceAccountId())
                        .withPublicKeyId(addedCloudAuthKey.getPublicKeyId())
                        .withPrivateKey(addedCloudAuthKey.getPrivateKey()),
                CLOUD_ACCOUNT_DUPLICATED);
    }

    @After
    public void teardown() {
        if (addedCloudAuthKey != null) {
            userSteps.onCloudAuthKeysSteps().deleteCloudAuthKey(appId, addedCloudAuthKey.getId());
        }
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
