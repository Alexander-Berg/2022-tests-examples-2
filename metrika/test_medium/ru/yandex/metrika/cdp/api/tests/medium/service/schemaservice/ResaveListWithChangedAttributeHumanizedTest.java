package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.Set;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.ListItem;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class ResaveListWithChangedAttributeHumanizedTest extends AbstractSchemaServiceSaveListTest {

    @Before
    public void testBody() {
        String newHumanized = "new humanized";
        Attribute attrToChangeHumanized = attr;

        //list saving
        customList = getCustomList();
        schemaService.saveList(getCounterId(), customList);
        customList.setAttributes(List.of(
                new Attribute(getCounterId(),
                        attrToChangeHumanized.getName(),
                        attrToChangeHumanized.getType(),
                        attrToChangeHumanized.getMultivalued(),
                        newHumanized)
        ));
        //resaving list with new humanized for attribute
        schemaService.saveList(getCounterId(), customList);

        //replacing humanized also for local items to compare later with data from ydb
        var itemsWithUpdatedHumanized = new ArrayList<ListItem>();
        for (var item : Objects.requireNonNull(customList.getItems())) {
            var attributes = new HashMap<Attribute, Set<String>>();
            for (var oldAttribute : item.getAttributeValues().entrySet()) {
                if (oldAttribute.getKey().getName().equals(attrToChangeHumanized.getName())) {
                    var newAttr = oldAttribute.getKey();
                    newAttr.setHumanized(newHumanized);
                    attributes.put(newAttr, oldAttribute.getValue());
                } else {
                    attributes.put(oldAttribute.getKey(), oldAttribute.getValue());
                }
            }
            item.setAttributeValues(attributes);
            itemsWithUpdatedHumanized.add(item);
        }
        expectedItems = itemsWithUpdatedHumanized;
        updateDataAboutCustomListAfterUploading();
        updateItemsInfoAfterUploading();
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var tests = new ArrayList<Object[]>();
        tests.addAll(getCommonListTests());
        tests.addAll(getItemsTests());
        return tests;
    }
}
