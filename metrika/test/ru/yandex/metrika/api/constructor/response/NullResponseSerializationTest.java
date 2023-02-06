package ru.yandex.metrika.api.constructor.response;

import java.util.Collections;
import java.util.Map;

import org.junit.Test;

import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;

public class NullResponseSerializationTest {

    /**
     * Default serialization behavior was changed at jackson 2.6.3 -> 2.9.1 migration
     */
    @Test
    public void mapWithNullValue() throws Exception {
        final Map<String, String> map = Collections.singletonMap("name", null);
        final String serialized = ObjectMappersFactory.getDefaultMapper().writeValueAsString(map);

        assertThat(serialized, equalTo("{\"name\":null}"));
    }

}
