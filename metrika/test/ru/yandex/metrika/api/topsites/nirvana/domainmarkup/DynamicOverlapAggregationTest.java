package ru.yandex.metrika.api.topsites.nirvana.domainmarkup;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import groovy.lang.Binding;
import groovy.lang.GroovyShell;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

@RunWith(Parameterized.class)
public class DynamicOverlapAggregationTest {

    public static final String SCRIPT_PATH = "/ru/yandex/metrika/topsites/nirvana/domain_markup/dynamic_overlap_aggregation.groovy";

    private GroovyShell groovyShell;
    private Data data;
    private Writer out;

    @Parameterized.Parameters(name = "data file name: {0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][] {
                { "site_type_data.json" },
                { "thematic_level_1_data.json" },
                { "thematic_level_2_data.json" }
        });
    }

    @Parameterized.Parameter
    public String dataFileName;

    @Before
    public void init() throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        data = objectMapper.readValue(getClass().getResource(dataFileName), Data.class);
        out = new Writer();

        Binding binding = new Binding();
        binding.setVariable("in0", data.getTasks());
        binding.setVariable("in1", data.getHoneypots());
        binding.setVariable("in2", Collections.singletonList(data.getStorage()));
        binding.setVariable("out", out);
        groovyShell = new GroovyShell(binding);
    }

    @Test
    public void test() throws IOException {
        try (Reader reader = new InputStreamReader(getClass().getResourceAsStream(SCRIPT_PATH))) {
            groovyShell.evaluate(reader);
        }
        Assert.assertEquals("", data.expectedResults, out.getData());
    }

    public static class Data {

        private List<Map<String, Object>> tasks;
        private List<Map<String, Object>> honeypots;
        private Map<String, Object> storage;
        private List<Map<String, Object>> expectedResults;

        public List<Map<String, Object>> getTasks() {
            return tasks;
        }

        public void setTasks(List<Map<String, Object>> tasks) {
            this.tasks = tasks;
        }

        public List<Map<String, Object>> getHoneypots() {
            return honeypots;
        }

        public void setHoneypots(List<Map<String, Object>> honeypots) {
            this.honeypots = honeypots;
        }

        public Map<String, Object> getStorage() {
            return storage;
        }

        public void setStorage(Map<String, Object> storage) {
            this.storage = storage;
        }

        public List<Map<String, Object>> getExpectedResults() {
            return expectedResults;
        }

        public void setExpectedResults(List<Map<String, Object>> expectedResults) {
            this.expectedResults = expectedResults;
        }
    }

    public static class Writer {

        private List<Object> data = new ArrayList<>();

        public void write(Object value) {
            data.add(value);
        }

        public List<Object> getData() {
            return data;
        }
    }
}
