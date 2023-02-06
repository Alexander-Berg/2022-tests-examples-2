package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class ResaveListWithoutItemsDoesNotChangeAlreadySavedItemsTest extends AbstractSchemaServiceSaveListTest {

    @Before
    public void testBody() {
        //list saving
        customList = getCustomList();
        schemaService.saveList(getCounterId(), customList);

        expectedItems = customList.getItems();
        customList.setItems(null);
        var tmpAttributeList = new ArrayList<>(customList.getAttributes());
        tmpAttributeList.add(new Attribute(getCounterId(), "new_attribute",
                AttributeType.TEXT, false, "Новый атрибут"));
        customList.setAttributes(tmpAttributeList);
        //resaving list with new attribute and without items
        schemaService.saveList(getCounterId(), customList);
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
