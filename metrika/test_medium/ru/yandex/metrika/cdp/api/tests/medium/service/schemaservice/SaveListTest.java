package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class SaveListTest extends AbstractSchemaServiceSaveListTest {

    @Parameterized.Parameter(2)
    public boolean withoutItems;

    @Before
    public void testBody() {
        customList = getCustomList();
        if (withoutItems) {
            customList.setItems(null);
        }
        schemaService.saveList(getCounterId(), customList);
        updateDataAboutCustomListAfterUploading();
        if (!withoutItems) {
            expectedItems = customList.getItems();
            updateItemsInfoAfterUploading();
        }
    }

    @Parameterized.Parameters(name = "{1}, without items: {2}")
    public static List<Object[]> getParameters() {
        var testList = new ArrayList<Object[]>();
        List.of(true, false).forEach(
                //common tests
                isWithoutItems -> getCommonListTests().forEach(
                        arrayOfTest -> testList.add(new Object[]{arrayOfTest[0], arrayOfTest[1], isWithoutItems})
                )
        );
        //tests of items
        getItemsTests().forEach(
                arrayOfTest -> testList.add(new Object[]{arrayOfTest[0], arrayOfTest[1], false})
        );
        return testList;
    }
}
