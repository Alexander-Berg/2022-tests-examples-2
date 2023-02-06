package ru.yandex.taxi.dmp.flink.test;

import lombok.Getter;
import lombok.ToString;

import ru.yandex.taxi.dmp.flink.config.Environment;
import ru.yandex.taxi.dmp.flink.config.FlinkAppArgs;

@ToString
public class TestArgs extends FlinkAppArgs {
    @Getter
    private final String testInTopic;
    @Getter
    private final String testOutTopic;

    public TestArgs(Environment environment) {
        super(environment);

        this.testInTopic = logbrokerTopics.getString("test_in");
        this.testOutTopic = logbrokerTopics.getString("test_out");
    }
}
