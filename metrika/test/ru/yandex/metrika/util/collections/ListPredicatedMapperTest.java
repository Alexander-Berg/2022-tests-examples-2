package ru.yandex.metrika.util.collections;

import java.util.List;

import com.google.common.collect.Lists;
import org.junit.Before;
import org.junit.Test;

import static junit.framework.Assert.assertEquals;

/**
 * @author jkee
 */

public class ListPredicatedMapperTest {

    ListPredicatedMapper<String, String> mapper;
    @Before
    public void setUp() throws Exception {
        mapper = ListPredicatedMapper.create("NULL", input -> F.map(input, input1 -> input1 + "_transformed"));
    }

    @Test
    public void testName() throws Exception {
        List<String> src = Lists.newArrayList("NULL", "ololo", "_NULL", "NULL_", "NULL");
        List<String> required = Lists.newArrayList("NULL", "ololo_transformed", "_NULL_transformed", "NULL__transformed", "NULL");
        List<String> result = mapper.map(src);
        assertEquals(required, result);
    }
}
