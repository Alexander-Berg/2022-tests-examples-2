package ru.yandex.metrika.util.json;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.util.collections.MapBuilder;

/**
 * @author jkee
 */

public class LinkingMapperFactoryTest {

    private final Map<String, TestClass> map = MapBuilder.<String, TestClass>builder()
            .put("alala", new TestClass("alala_text"))
            .put("ololo", new TestClass("ololo_text"))
            .put("1", new TestClass("1_text"))
            .build();

    @Test
    public void testLinking() throws Exception {
        LinkerProviderString<TestClass> repository = LinkerProviderString.create(TestClass.class, id -> map.get(id));
        ObjectMapper mappingMapper = LinkingMapperFactory.getLinkingMapper(repository);
        Object o = mappingMapper.readValue("[\"alala\", \"ololo\", 1]", new TypeReference<List<TestClass>>() {
        });
        ArrayList<TestClass> reference = Lists.newArrayList(
                new TestClass("alala_text"), new TestClass("ololo_text"), new TestClass("1_text")
        );
        Assert.assertEquals(reference, o);
    }

    @Test
    public void testName() throws Exception {
        //Function<String, TestClass> f = map::get;
        LinkerProvider<String, TestClass> provider = LinkerProvider.create(TestClass.class, String.class, id -> map.get(id));
        ObjectMapper mappingMapper = LinkingMapperFactory.getMappingMapper(provider);
        Object o = mappingMapper.readValue("[\"alala\", \"ololo\"]", new TypeReference<List<TestClass>>() {
        });
        ArrayList<TestClass> reference = Lists.newArrayList(new TestClass("alala_text"), new TestClass("ololo_text"));
        Assert.assertEquals(reference, o);
    }

    public static class TestClass {
        String value;

        public TestClass(String value) {
            this.value = value;
        }

        public TestClass() {
        }

        public String getValue() {
            return value;
        }

        public void setValue(String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return "TestClass{" +
                    "value='" + value + '\'' +
                    '}';
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof TestClass)) return false;

            TestClass testClass = (TestClass) o;

            return value != null ? value.equals(testClass.value) : testClass.value == null;
        }

        @Override
        public int hashCode() {
            return value != null ? value.hashCode() : 0;
        }
    }

}
