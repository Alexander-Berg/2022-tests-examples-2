package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.cloud;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudExport;
import ru.yandex.metrika.mobmet.cloud.model.CloudTableType;
import ru.yandex.metrika.mobmet.cloud.model.ExportValidationResult;
import ru.yandex.metrika.mobmet.cloud.model.ExportValidationResultInnerField;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_REPLICATED_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.TABLE_FOR_FUNCTIONAL_TESTS_ILLEGAL_SCHEMA;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCloudExport;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.editorCloudAuthKey;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.mobmet.cloud.model.CloudTableType.EXISTING;
import static ru.yandex.metrika.mobmet.cloud.model.CloudTableType.NEW;

@Features(Requirements.Feature.Management.CLOUD)
@Stories({
        Requirements.Story.CloudExports.VALIDATION
})
@Title("Валидация экспорта в существующую таблицы")
@RunWith(Parameterized.class)
public class CloudExistingTableValidationTest {

    private static final User USER = Users.SIMPLE_USER;
    private static final UserSteps userSteps = UserSteps.onTesting(USER);

    private static long appId;
    private static CloudAuthKey addedCloudAuthKey;

    @Parameter
    public CloudTableType tableType;
    @Parameter(1)
    public String tableName;
    @Parameter(2)
    public ExportValidationResult expectedValidationResult;

    @Parameters
    public static Collection<Object[]> parameters() {
        return asList(
                params(EXISTING, TABLE_FOR_FUNCTIONAL_TESTS_ILLEGAL_SCHEMA,
                        new ExportValidationResult()
                                .withStatus("illegal_table_schema")
                                .withAbsentCloudFields(asList(
                                        new ExportValidationResultInnerField()
                                                .withName("appmetrica_device_id")
                                                .withExpectedType("UInt64"),
                                        new ExportValidationResultInnerField()
                                                .withName("event_timestamp")
                                                .withExpectedType("UInt64")
                                ))
                                .withFieldsWithIllegalType(asList(
                                        new ExportValidationResultInnerField()
                                                .withName("event_receive_datetime")
                                                .withExpectedType("DateTime")
                                                .withActualCloudType("UInt64")
                                ))),
                params(EXISTING, TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA, new ExportValidationResult().withStatus("ok"
                )),
                params(EXISTING, "NOT_EXISTING_TABLE", new ExportValidationResult().withStatus("table_access_denied")),
                params(NEW, null, new ExportValidationResult().withStatus("ok")),
                params(NEW, TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA,
                        new ExportValidationResult().withStatus("table_already_exists"))
        );
    }

    private static Object[] params(CloudTableType tableType, String tableName,
                                   ExportValidationResult expectedValidationResponse) {
        return new Object[]{tableType, tableName, expectedValidationResponse};
    }

    @BeforeClass
    public static void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedCloudAuthKey = userSteps.onCloudAuthKeysSteps().createCloudAuthKey(appId, editorCloudAuthKey());
    }

    @Test
    public void testValidation() {
        CloudExport export = defaultCloudExport()
                .withClusterId(CLOUD_REPLICATED_SHARD_CLUSTER)
                .withTableType(tableType)
                .withClickhouseTableName(tableName)
                .withFields(asList("event_name", "event_timestamp", "event_receive_datetime"));
        ExportValidationResult actual = userSteps.onCloudExportsSteps().validate(appId, export);
        assertThat("Результат валидации экспорта в облако эквивалентен ожидаемому", actual,
                equivalentTo(expectedValidationResult));
    }

    @AfterClass
    public static void teardown() {
        if (addedCloudAuthKey != null) {
            userSteps.onCloudAuthKeysSteps().deleteCloudAuthKey(appId, addedCloudAuthKey.getId());
        }
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
