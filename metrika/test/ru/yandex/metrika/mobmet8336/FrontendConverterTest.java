package ru.yandex.metrika.mobmet8336;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;

@Ignore
public class FrontendConverterTest {

    @Test
    public void check() {
        FrontendConverter converter = new FrontendConverter();
        // ["{\"filters\":{\"regionGeo\":[[\"225\",\"1\"]]}}"]
        String result = converter.convert("{\"filters\":{\"regionGeo\":[[\"225\",\"1\"]]}}");
        Assert.assertEquals("{ \"filters\": {\"regionGeo\":{\"inverted\":false,\"values\":[{\"tree\":[\"225\",\"1\"]}]}} }", result);
    }
}
