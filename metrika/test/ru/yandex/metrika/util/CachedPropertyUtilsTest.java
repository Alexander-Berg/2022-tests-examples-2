package ru.yandex.metrika.util;

import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.anyString;
import static org.mockito.Mockito.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class CachedPropertyUtilsTest {

    private CachedPropertyUtils propertyUtils;

    @Before
    public void setup() {
        PropertyUtils mock = mock(PropertyUtils.class);
        when(mock.getProperty(anyString(), eq(String.class))).thenReturn("val");
        when(mock.getProperty(anyString(), eq(Integer.class))).thenReturn(123);
        propertyUtils = new CachedPropertyUtils(mock);
        propertyUtils.init();
    }

    @Test
    public void getProperty() {
        assertEquals(propertyUtils.getProperty("test", String.class), "val");
        assertEquals(propertyUtils.getProperty("test", Integer.class), (Integer)123);
    }
}
