package ru.yandex.metrika.util.json;

import java.util.Collections;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.jkee.gtree.Forest;
import org.jkee.gtree.Tree;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

/**
 * @author jkee
 */

public class TreeSerializerTest2 {

    public static class TestEntity {
        public final int id;

        public TestEntity(int id) {
            this.id = id;
        }

        @Override
        public String toString() {
            return '{' +
                           "id=" + id +
                           '}';
        }
    }

    ObjectMapper jacksonObjectMapper;

    @Before
    public void setUp() throws Exception {
        jacksonObjectMapper = new ObjectMapper();
        jacksonObjectMapper.registerModule(TreeSerializer.JACKSON_MODULE);
    }

    @Test
    public void testSer() throws Exception {
        Tree<TestEntity> testEntityTree = new Tree<>(new TestEntity(100));
        testEntityTree.addChild(new Tree<>(new TestEntity(200)));
        Tree<TestEntity> child = new Tree<>(new TestEntity(300));
        child.addChild(new Tree<>(new TestEntity(400)));
        testEntityTree.addChild(child);
        String s = jacksonObjectMapper.writeValueAsString(testEntityTree);
        Assert.assertEquals("{\"id\":100,\"chld\":[{\"id\":200},{\"id\":300,\"chld\":[{\"id\":400}]}]}", s);
    }

    @Test
    public void testSerForest() throws Exception {
        Tree<TestEntity> testEntityTree = new Tree<>(new TestEntity(100));
        testEntityTree.addChild(new Tree<>(new TestEntity(200)));
        Tree<TestEntity> child = new Tree<>(new TestEntity(300));
        child.addChild(new Tree<>(new TestEntity(400)));
        testEntityTree.addChild(child);
        Forest<TestEntity> forest = new Forest<>(Collections.singletonList(testEntityTree));
        String s = jacksonObjectMapper.writeValueAsString(forest);
        Assert.assertEquals("[{\"id\":100,\"chld\":[{\"id\":200},{\"id\":300,\"chld\":[{\"id\":400}]}]}]", s);
    }
}
