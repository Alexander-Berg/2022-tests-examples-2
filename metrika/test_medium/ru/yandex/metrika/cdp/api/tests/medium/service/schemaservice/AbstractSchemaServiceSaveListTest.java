package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.CustomList;
import ru.yandex.metrika.cdp.dto.schema.ListItem;
import ru.yandex.metrika.cdp.dto.schema.ListType;
import ru.yandex.metrika.util.collections.F;

import static java.util.stream.Collectors.toMap;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

public abstract class AbstractSchemaServiceSaveListTest extends AbstractSchemaServiceParameterizedTest {

    CustomList customList;
    AttributeType attributeType;
    Map<String, Attribute> attributesLoaded;
    Map<String, ListItem> customListItemsFromYDB;
    List<ListItem> expectedItems;

    static protected Collection<Object[]> getCommonListTests() {
        return Arrays.asList(
                new Object[][]{
                        {c(test -> assertNotNull(test.attributeType)),
                                "Тест наличия загруженного списка"},
                        {c(test -> assertEquals(test.customList.getHumanized(), test.attributeType.getHumanized())),
                                "Тест корректности названия списка"},
                        {c(test -> assertEquals(AttributeType.Group.CUSTOM_LIST, test.attributeType.getGroup())),
                                "Тест типа загруженного списка"},
                        {c(test -> assertTrue(test.customList.getAttributes().size() <=
                                test.attributesLoaded.size())), "Тест количества атрибутов загруженного списка"},
                        {c(test -> {
                            for (var attribute : test.customList.getAttributes()) {
                                assertTrue(isAttributeEqual(attribute, test.attributesLoaded.get(attribute.getName())));
                            }
                        }), "Тест корректности загруженных атрибутов"}
                });
    }

    static protected Collection<Object[]> getItemsTests() {
        return Arrays.asList(
                new Object[][]{
                        {c(test -> assertEquals(test.customListItemsFromYDB.size(),
                                Objects.requireNonNull(test.expectedItems).size())),
                                "Тест количества загруженных элементов списка"},
                        {c(test -> {
                            for (var item : Objects.requireNonNull(test.expectedItems)) {
                                assertTrue("expect item: " + item +
                                                " but got: " + test.customListItemsFromYDB.get(item.getName()),
                                        areListItemsEqual(test.customListItemsFromYDB.get(item.getName()), item));
                            }
                        }), "Тест корректности загруженных элементов списка"}
                }
        );
    }

    protected void updateDataAboutCustomListAfterUploading() {
        attributeType = schemaService
                .getAllTypes(getCounterId())
                .stream()
                .filter(x -> x.getName().equals(customList.getName()))
                .findFirst()
                .orElse(null);
        attributesLoaded = schemaService
                .getList(getCounterId(), ListType.CUSTOM, customList.getName())
                .getAttributes()
                .stream()
                .collect(toMap(Attribute::getName, F.id()));
    }

    protected void updateItemsInfoAfterUploading() {
        customListItemsFromYDB = Objects.requireNonNull(
                schemaService.getList(getCounterId(), ListType.CUSTOM, customList.getName()).getItems()
        )
                .stream()
                .collect(toMap(ListItem::getName, x -> x));
    }

    private static Consumer<AbstractSchemaServiceSaveListTest> c(Consumer<AbstractSchemaServiceSaveListTest> x) {
        return x;
    }
}
