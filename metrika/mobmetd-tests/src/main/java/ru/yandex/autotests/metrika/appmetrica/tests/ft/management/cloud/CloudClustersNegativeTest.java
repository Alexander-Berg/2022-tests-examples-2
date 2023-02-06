package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ACCOUNT_NOT_FOUND_IN_CLOUD;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ACCOUNT_NOT_FOUND_IN_PG;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ACCOUNT_WITHOUT_GRANTS_IN_CLOUD;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ACCOUNT_WITHOUT_KEY_IN_CLOUD;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_ACCOUNT_WITH_REMOVED_FOLDER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CLOUD_DENIED_VIEWER_ACCOUNT;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudClusters.GET_LIST
})
@Title("Получение списка кластеров (негативный)")
@RunWith(Parameterized.class)
public class CloudClustersNegativeTest {
    private static final String ACCOUNT_REMOVED_FROM_APPMETRICA =
            "removed_from_appmetrica_dhx4GZaQdIEiAgNla7u";
    private static final String ACCOUNT_REMOVED_FROM_CLOUD =
            "ajehso41uk2qes44l5j0";
    private static final String ACCOUNT_WITHOUT_KEY_IN_CLOUD =
            "ajerl6k9oc16c50f1arc";
    private static final String ACCOUNT_WITHOUT_GRANTS_IN_CLOUD =
            "ajeqsi5m961du9gllqd8";
    private static final String ACCOUNT_WITH_INVALID_FOLDER_IN_CLOUD =
            "ajedr57fhpcfqtq2kv92";
    private static final String ACCOUNT_VIEWER =
            "aje0thp9hesjfgvb2g7k";

    private static final User USER = Users.SUPER_LIMITED;
    private static final UserSteps userSteps = UserSteps.onTesting(USER);

    @Parameter
    public String desc;

    @Parameter(1)
    public String serviceAccountId;

    @Parameter(2)
    public ManagementError expectedError;

    @Parameters(name = "{0}")
    public static List<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(params("Аккаунт удалён из аппметрики", ACCOUNT_REMOVED_FROM_APPMETRICA,
                        CLOUD_ACCOUNT_NOT_FOUND_IN_PG))
                .add(params("Аккаунт удалён из облака", ACCOUNT_REMOVED_FROM_CLOUD, CLOUD_ACCOUNT_NOT_FOUND_IN_CLOUD))
                .add(params("Аккаунт без ключа в облаке", ACCOUNT_WITHOUT_KEY_IN_CLOUD,
                        CLOUD_ACCOUNT_WITHOUT_KEY_IN_CLOUD))
                .add(params("Аккаунт без прав в облаке", ACCOUNT_WITHOUT_GRANTS_IN_CLOUD,
                        CLOUD_ACCOUNT_WITHOUT_GRANTS_IN_CLOUD))
                .add(params("Аккаунт с правами viewer", ACCOUNT_VIEWER,
                        CLOUD_DENIED_VIEWER_ACCOUNT))
                .add(params("Аккаунт с некоректным каталогом", ACCOUNT_WITH_INVALID_FOLDER_IN_CLOUD,
                        CLOUD_ACCOUNT_WITH_REMOVED_FOLDER))
                .build();
    }

    private static Object[] params(String desc, String serviceAccountId, ManagementError error) {
        return new Object[]{desc, serviceAccountId, error};
    }

    @Test
    public void testGetClusterAndExpectError() {
        userSteps.onCloudClustersSteps().getCloudClustersAndExpectError(
                PUSH_SAMPLE.get(ID), serviceAccountId, expectedError);
    }
}
