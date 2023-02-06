package ru.yandex.metrika.cdp.api.validation.util;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;

public class AttributesCreationUtil {

    public static final String CUSTOM_LIST_NAME = "customList";
    public static final String CUSTOM_LIST_ITEM_NAME = "itemName";

    public static Attribute dateAttribute() {
        return new Attribute(1,"dateAttribute", AttributeType.DATE, false, "");
    }

    public static Attribute numericAttribute() {
        return new Attribute(1, "numericAttribute", AttributeType.NUMERIC, false, "");
    }

    public static Attribute emailAttribute() {
        return new Attribute(1, "emailAttribute", AttributeType.EMAIL, false, "");
    }

    public static Attribute attributeWithListType(String customListName) {
        return new Attribute(1,customListName + "Attribute", AttributeType.createCustom(customListName, ""), false, "");
    }

    public static String attributeLocation(Attribute attribute) {
        return "attributeValues." + attribute.getName();
    }
}
