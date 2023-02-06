package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.List;
import java.util.Map;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.ApiException;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.schema.ListItem;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;
import ru.yandex.metrika.util.collections.Lists2;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class SchemaServiceNegativeTests extends AbstractSchemaServiceTest {

    @Test(expected = ApiException.class)
    public void UpdateAttributeFailureOnMultivaluedChangedTest() {
        schemaService.saveAttributes(getCounterId(), EntityNamespace.ORDER, List.of(attr2));
        var attr2WithForbiddenChanges = new Attribute(getCounterId(),
                attr2.getName(),
                attr2.getType(),
                !attr2.getMultivalued(),
                attr2.getHumanized());
        schemaService.saveAttributes(getCounterId(), EntityNamespace.ORDER, List.of(attr2WithForbiddenChanges));
    }

    @Test(expected = ApiException.class)
    public void UpdateAttributeFailureOnTypeChangedTest() {
        schemaService.saveAttributes(getCounterId(), EntityNamespace.ORDER, List.of(attr2));
        var attr2WithForbiddenChanges = new Attribute(getCounterId(),
                attr2.getName(),
                AttributeType.DATE,
                attr2.getMultivalued(),
                attr2.getHumanized());
        schemaService.saveAttributes(getCounterId(), EntityNamespace.ORDER, List.of(attr2WithForbiddenChanges));
    }

    @Test(expected = ApiException.class)
    public void SaveAttributeFailureOnClashWithSystemAttributes() {
        schemaService.saveAttributes(
                getCounterId(),
                EntityNamespace.CONTACT,
                List.of(
                        new Attribute("name", "", AttributeType.TEXT, false)
                )
        );
    }

    @Test(expected = ApiException.class)
    public void SaveAttributeFailureOnDuplicatedNames() {
        schemaService.saveAttributes(
                getCounterId(),
                EntityNamespace.CONTACT,
                List.of(
                        new Attribute("my_attr", "", AttributeType.TEXT, false),
                        new Attribute("my_attr", "", AttributeType.DATE, false)
                )
        );
    }

    @Test(expected = ApiException.class)
    public void SaveListWithChangedAttributeTypes() {
        var customList = getCustomList();
        schemaService.saveList(getCounterId(), customList);

        customList.setAttributes(List.of(
                new Attribute(getCounterId(), attr.getName(), AttributeType.DATETIME, false, "")
        ));

        schemaService.saveList(getCounterId(), customList);
    }

    @Test(expected = ApiException.class)
    public void SaveListFailureOnDuplicatedListItems() {
        var customList = getCustomList();
        customList.setItems(List.of(
                new ListItem("item1", "", Map.of()),
                new ListItem("item1", "", Map.of())
        ));

        schemaService.saveList(getCounterId(), customList);
    }

    @Test(expected = ApiException.class)
    public void SaveListFailureOnDuplicatedAttributes() {
        var customList = getCustomList();
        customList.setAttributes(
                Lists2.concat(
                        customList.getAttributes(),
                        List.of(
                                new Attribute("my_attr", "", AttributeType.TEXT, false),
                                new Attribute("my_attr", "", AttributeType.DATE, false)
                        )
                )
        );

        schemaService.saveList(getCounterId(), customList);
    }

    @Test(expected = ApiException.class)
    public void SchemaServiceSaveOrderStatusesFailureOnDuplicatedIds() {
        var orderStatusList = List.of(
                new OrderStatus("od1", "Статус заказа аналогичный 'В работе'", OrderStatusType.IN_PROGRESS),
                new OrderStatus("od1", "Статус заказа аналогичный 'Оплачен'", OrderStatusType.PAID)
        );

        schemaService.saveOrderStatuses(getCounterId(), orderStatusList);
    }
}
