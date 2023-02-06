package ru.yandex.metrika.mobmet.crash.ios;

import org.junit.Assert;
import org.junit.Test;

public class BinaryImageUUIDUtilsTest {

    @Test
    public void toInternal() {
        String actual = BinaryImageUUIDUtils.toInternalFormat("9DCB0B84-3FE9-31E4-87C6-EE731464217E");
        Assert.assertEquals("9dcb0b843fe931e487c6ee731464217e", actual);
    }

    @Test
    public void toExternal() {
        String actual = BinaryImageUUIDUtils.toExternalFormat("9dcb0b843fe931e487c6ee731464217e");
        Assert.assertEquals("9DCB0B84-3FE9-31E4-87C6-EE731464217E", actual);
    }

    @Test
    public void checkValid() {
        Assert.assertTrue(BinaryImageUUIDUtils.isValidUUID("a73e5935-df86-4c10-b12b-0e71e8dd4cf6"));
    }
}
