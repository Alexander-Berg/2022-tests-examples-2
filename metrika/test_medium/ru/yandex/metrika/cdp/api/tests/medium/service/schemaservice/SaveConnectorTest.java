package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.time.Instant;
import java.time.temporal.ChronoField;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import com.yandex.ydb.table.query.Params;
import org.junit.Assert;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;

import ru.yandex.metrika.api.ApiException;
import ru.yandex.metrika.cdp.common.FieldNames;
import ru.yandex.metrika.cdp.dto.schema.connector.Connector;
import ru.yandex.metrika.cdp.dto.schema.connector.ConnectorStatus;
import ru.yandex.metrika.cdp.dto.schema.connector.ConnectorType;
import ru.yandex.metrika.cdp.dto.schema.connector.UpdateConnector;
import ru.yandex.metrika.cdp.dto.schema.connector.UpdateConnectorStatus;
import ru.yandex.metrika.cdp.dto.schema.connector.bitrix.BitrixConnectorAttributes;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class SaveConnectorTest extends AbstractSchemaServiceTest {

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Autowired
    private YdbTemplate ydbTemplate;

    @Parameter
    public String testName;

    @Parameter(value = 1)
    public ConnectorType type;

    @Parameter(value = 2)
    public Connector before;

    @Parameter(value = 3)
    public UpdateConnector update;

    @Parameter(value = 4)
    public Connector expected;

    @Parameter(value = 5)
    public boolean succeeded;

    @Before
    public void cleanTables() {
        String tablePrefix = schemaDao.getTablePrefix();
        ydbTemplate.execute("" +
                        "PRAGMA TablePathPrefix = \"" + tablePrefix + "\";\n" +
                        "DELETE FROM " + SchemaDaoYdb.CONNECTORS_TABLE + "\n" +
                        "WHERE " + FieldNames.Connector.COUNTER_ID + " = " + getCounterId() + ";\n",
                Params.empty(),
                "SaveConnectorTest.cleanTables()",
                QueryExecutionContext.write()
        );
        ydbTemplate.execute("" +
                        "PRAGMA TablePathPrefix = \"" + tablePrefix + "\";\n" +
                        "DELETE FROM " + SchemaDaoYdb.BITRIX_CONNECTORS_ATTRIBUTES_TABLE + "\n" +
                        "WHERE " + FieldNames.BitrixConnectorAttributes.COUNTER_ID + " = " + getCounterId() + ";\n",
                Params.empty(),
                "SaveConnectorTest.cleanTables()",
                QueryExecutionContext.write()
        );
    }

    @Test
    public void testBody() {
        Assert.assertEquals(0, schemaDao.getConnectors(List.of(getCounterId()), ConnectorType.BITRIX).size());
        Assert.assertEquals(0, schemaDao.getBitrixConnectorAttributes(List.of(getCounterId())).size());
        if (before != null) {
            schemaDao.saveConnectors(List.of(before));
            if (before.getAttributes() instanceof BitrixConnectorAttributes attributes) {
                schemaDao.saveBitrixConnectorAttributes(List.of(attributes));
            }
        }
        try {
            schemaService.saveConnector(getCounterId(), update);
            Assert.assertTrue(succeeded);
        } catch (ApiException e) {
            Assert.assertFalse(succeeded);
        }
        Connector after = schemaService.getConnector(getCounterId(), type);
        Assert.assertEquals(expected, after);
    }

    @Parameters(name = "{0}")
    public static Collection<Object[]> parameters() {
        List<Object[]> parameters = new ArrayList<>();

        ConnectorType bitrix = ConnectorType.BITRIX;
        String validUrl = "valid.url";
        Instant now = Instant.now().with(ChronoField.NANO_OF_SECOND, 0);

        UpdateConnector validAddUpdate = new UpdateConnector(bitrix, validUrl, UpdateConnectorStatus.ADD, null);
        BitrixConnectorAttributes defaultBitrixAttributes = new BitrixConnectorAttributes(getCounterId());
        Connector validExpected = new Connector(getCounterId(), validUrl, bitrix, ConnectorStatus.NEW, Instant.EPOCH, defaultBitrixAttributes);
        parameters.add(new Object[]{"Valid add", bitrix, null, validAddUpdate, validExpected, true});

        BitrixConnectorAttributes bitrixAttributesWithDisabledLeads = new BitrixConnectorAttributes(getCounterId(), false);
        Connector validConnectedWithDisabledLeads =
                new Connector(getCounterId(), validUrl, bitrix, ConnectorStatus.CONNECTED, now, bitrixAttributesWithDisabledLeads);
        UpdateConnector deleteUpdate = new UpdateConnector(bitrix, null, UpdateConnectorStatus.DELETE, null);
        Connector deletedValidConnectedWithDisabledLeads =
                new Connector(getCounterId(), validUrl, bitrix, ConnectorStatus.DELETED, now, bitrixAttributesWithDisabledLeads);
        parameters.add(new Object[]{"Valid delete", bitrix, validConnectedWithDisabledLeads, deleteUpdate, deletedValidConnectedWithDisabledLeads, true});

        Connector notConnected = new Connector(getCounterId(), bitrix);
        parameters.add(new Object[]{"Delete not connected", bitrix, null, deleteUpdate, notConnected, true});

        parameters.add(new Object[]{"Delete already deleted", bitrix, deletedValidConnectedWithDisabledLeads, deleteUpdate, deletedValidConnectedWithDisabledLeads, true});

        Connector validConnected = new Connector(getCounterId(), validUrl, bitrix, ConnectorStatus.CONNECTED, now, defaultBitrixAttributes);
        UpdateConnector disableLeadsUpdate = new UpdateConnector(bitrix, null, null,
                new BitrixConnectorAttributes(getCounterId(), false));
        parameters.add(new Object[]{"Disable leads", bitrix, validConnected, disableLeadsUpdate, validConnectedWithDisabledLeads, true});

        UpdateConnector enableLeadsUpdate = new UpdateConnector(bitrix, null, null,
                new BitrixConnectorAttributes(getCounterId(), true));
        parameters.add(new Object[]{"Enable leads", bitrix, validConnectedWithDisabledLeads, enableLeadsUpdate, validConnected, true});

        UpdateConnector changeUrlUpdate = new UpdateConnector(bitrix, validUrl + validUrl, null, null);
        parameters.add(new Object[]{"Unsuccessful url change", bitrix, validConnectedWithDisabledLeads, changeUrlUpdate, validConnectedWithDisabledLeads, false});

        UpdateConnector addUpdateWithoutUrl = new UpdateConnector(bitrix, null, UpdateConnectorStatus.ADD, null);
        parameters.add(new Object[]{"Unsuccessful add without url", bitrix, null, addUpdateWithoutUrl, notConnected, false});

        UpdateConnector deleteWithDisablingLeadsUpdate = new UpdateConnector(bitrix, null, UpdateConnectorStatus.DELETE,
                new BitrixConnectorAttributes(getCounterId(), false));
        Connector deletedValidConnected = new Connector(getCounterId(), validUrl, bitrix, ConnectorStatus.DELETED, now,
                new BitrixConnectorAttributes(getCounterId(), false));
        parameters.add(new Object[]{"Delete with disabling leads", bitrix, validConnected, deleteWithDisablingLeadsUpdate, deletedValidConnected, true});

        return parameters;
    }
}
