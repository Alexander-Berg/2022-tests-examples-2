package ru.yandex.metrika.util.dao;

import java.util.Objects;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class JsonPropertyConverterTest {

    private final JsonPropertyConverter jsonPropertyConverter = new JsonPropertyConverter(CustomClass.class);

    private CustomClass object;
    private String json;

    @Before
    public void init() {
        object = new CustomClass();
        object.setFirstProp("firstValue");
        object.setSecondProp("secondValue");

        json = "{\"firstProp\":\"firstValue\",\"secondProp\":\"secondValue\"}";
    }

    @Test
    public void testConvertToJdbc() {
        Assert.assertEquals(json, jsonPropertyConverter.convertToJdbc(object));
    }

    @Test
    public void testConvertFromJdbc() {
        Assert.assertEquals(object, jsonPropertyConverter.convertFromJdbc(json));
    }

    public static class CustomClass {

        private String firstProp;
        private String secondProp;

        public String getFirstProp() {
            return firstProp;
        }

        public void setFirstProp(String firstProp) {
            this.firstProp = firstProp;
        }

        public String getSecondProp() {
            return secondProp;
        }

        public void setSecondProp(String secondProp) {
            this.secondProp = secondProp;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            CustomClass that = (CustomClass) o;
            return Objects.equals(firstProp, that.firstProp) &&
                    Objects.equals(secondProp, that.secondProp);
        }

        @Override
        public int hashCode() {
            return Objects.hash(firstProp, secondProp);
        }
    }
}
