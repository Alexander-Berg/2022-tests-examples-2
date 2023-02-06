package ru.yandex.metrika.ui.controller.constructor;

import java.util.List;

import com.google.common.collect.Lists;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.constructor.FieldConverter;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;

/**
 * @author jkee
 */

public class FieldConverterTest {

    public static class TestEntity {
        int intField;
        String stringField;
        String stringField2;

        TestEntity child;

        List<TestEntity> entityList;

        public TestEntity() {
        }

        public TestEntity(int intField, String stringField) {
            this.intField = intField;
            this.stringField = stringField;
        }

        public int getIntField() {
            return intField;
        }

        public void setIntField(int intField) {
            this.intField = intField;
        }

        public String getStringField() {
            return stringField;
        }

        public void setStringField(String stringField) {
            this.stringField = stringField;
        }

        public String getStringField2() {
            return stringField2;
        }

        public void setStringField2(String stringField2) {
            this.stringField2 = stringField2;
        }

        public TestEntity getChild() {
            return child;
        }

        public void setChild(TestEntity child) {
            this.child = child;
        }

        public List<TestEntity> getEntityList() {
            return entityList;
        }

        public void setEntityList(List<TestEntity> entityList) {
            this.entityList = entityList;
        }
    }

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup();
    }

    @Test
    public void testSimpleFilter() throws Exception {
        String filter = "stringField";
        FieldConverter converter = new FieldConverter(filter);
        TestEntity src = new TestEntity(1, "ololo");
        TestEntity dest = converter.filterResponse(src);
        assertEquals(0, dest.intField);
        assertEquals("ololo", dest.stringField);
    }

    @Test
    public void testFilter2() throws Exception {
        String filter = "stringField,intField";
        FieldConverter converter = new FieldConverter(filter);
        TestEntity src = new TestEntity(1, "ololo");
        src.setStringField2("ololo2");
        TestEntity dest = converter.filterResponse(src);
        assertEquals(1, dest.intField);
        assertEquals("ololo", dest.stringField);
        assertEquals(null, dest.stringField2);
    }

    @Test
    public void testFilter3() throws Exception {
        String filter = "stringField,child/intField";
        FieldConverter converter = new FieldConverter(filter);
        TestEntity src = new TestEntity(1, "ololo");
        TestEntity srcChild = new TestEntity(2, "alala");
        src.setChild(srcChild);
        TestEntity dest = converter.filterResponse(src);
        assertEquals(0, dest.intField);
        assertEquals("ololo", dest.stringField);
        assertEquals(2, dest.child.getIntField());
        assertEquals(null, dest.child.getStringField());
        assertEquals(null, dest.child.getStringField2());
    }

    @Test
    public void testFilter4() throws Exception {
        String filter = "stringField,child(intField,stringField)";
        FieldConverter converter = new FieldConverter(filter);
        TestEntity src = new TestEntity(1, "ololo");
        TestEntity srcChild = new TestEntity(2, "alala");
        srcChild.stringField2 = "ilili";
        src.setChild(srcChild);
        TestEntity dest = converter.filterResponse(src);
        assertEquals(0, dest.intField);
        assertEquals("ololo", dest.stringField);
        assertEquals(2, dest.child.getIntField());
        assertEquals("alala", dest.child.getStringField());
        assertEquals(null, dest.child.getStringField2());
    }

    @Test
    public void testFilterList() throws Exception {
        String filter = "entityList(intField)";
        FieldConverter converter = new FieldConverter(filter);
        TestEntity src = new TestEntity(1, "ololo");
        TestEntity srcChild1 = new TestEntity(2, "alala");
        TestEntity srcChild2 = new TestEntity(3, "alalza");
        src.setEntityList(Lists.newArrayList(srcChild1, srcChild2));
        TestEntity dest = converter.filterResponse(src);
        assertEquals(2, dest.getEntityList().size());
        assertEquals(2, dest.getEntityList().get(0).intField);
        assertEquals(3, dest.getEntityList().get(1).intField);
    }

}
