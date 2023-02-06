package ru.yandex.metrika.util.dao;

import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.apache.commons.lang3.reflect.TypeUtils;
import org.junit.Assert;
import org.junit.Test;

public class JsonPropertyConverterGenericTest {

    private final JsonPropertyConverter jsonPropertyConverter = new JsonPropertyConverter(
            TypeUtils.parameterize(Map.class, String.class,  TypeUtils.parameterize(List.class, String.class))
    );

    private final Map<String, List<String>> object = ImmutableMap.of(
            "key1", ImmutableList.of("val1", "val2"),
            "key2", ImmutableList.of("val3", "val4")
    );

    private final String json = "{\"key1\":[\"val1\",\"val2\"],\"key2\":[\"val3\",\"val4\"]}";

    @Test
    public void testConvertToJdbc() {
        Assert.assertEquals(json, jsonPropertyConverter.convertToJdbc(object));
    }

    @Test
    public void testConvertFromJdbc() {
        Assert.assertEquals(object, jsonPropertyConverter.convertFromJdbc(json));
    }
}
