package ru.yandex.metrika.util.dao;

import org.junit.Assert;
import org.junit.Test;

public class EnumPropertyConverterTest {

    private final EnumPropertyConverter<Enum> enumPropertyConverter = new EnumPropertyConverter<>(Enum.class);

    @Test
    public void testConvertToJdbc() {
        Assert.assertEquals("FIRST", enumPropertyConverter.convertToJdbc(Enum.FIRST));
        Assert.assertEquals("SECOND", enumPropertyConverter.convertToJdbc(Enum.SECOND));
    }

    @Test
    public void testConvertFromJdbc() {
        Assert.assertEquals(Enum.FIRST, enumPropertyConverter.convertFromJdbc("FIRST"));
        Assert.assertEquals(Enum.SECOND, enumPropertyConverter.convertFromJdbc("SECOND"));
    }

    public enum Enum {
        FIRST,
        SECOND
    }
}
