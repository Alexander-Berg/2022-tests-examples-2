package ru.yandex.taxi.dmp.flink;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.config.Environment;
import ru.yandex.taxi.dmp.flink.config.FlinkAppArgs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class AbstractConfiguredJobTest {
    public static class TestArgs extends FlinkAppArgs {
        public TestArgs(Environment environment) {
            super(environment);
        }
    }

    public static class TestJob extends AbstractConfiguredJob<TestArgs> {
        @Override
        public void configure(StreamExecutionEnvironment env) {

        }
    }

    @Test
    void testJobCreation() {
        var job = TestJob.createJob(TestJob.class, Environment.TESTING);
        assertNotNull(job);
        assertEquals("test-service", job.getAppArgs().getServiceName());
    }
}
