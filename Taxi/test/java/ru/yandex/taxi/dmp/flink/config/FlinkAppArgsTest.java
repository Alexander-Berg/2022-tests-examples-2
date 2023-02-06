package ru.yandex.taxi.dmp.flink.config;

import java.util.Map;

import lombok.Getter;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class FlinkAppArgsTest {
    private static class TestArgs extends FlinkAppArgs {
        @Getter private final String subscriptionsTopic;
        @Getter private final String pinsTopic;
        @Getter private final String offersTopic;

        private TestArgs(Environment environment) {
            super(environment);

            this.subscriptionsTopic = logbrokerTopics.getString("subscriptions");
            this.pinsTopic = logbrokerTopics.getString("pins");
            this.offersTopic = optional(logbrokerTopics, "offers").orElse(null);
        }
    }


    @Test
    void parseHocon() {
        var args = new TestArgs(Environment.TESTING);

        // from constructor.arg
        assertEquals(Environment.TESTING, args.environment);

        // from test/resources/application.conf
        assertEquals("test-service", args.serviceName);

        // from main/resources/common.conf
        assertEquals("s3://taxi-test-service/flink-checkpoint", args.checkpointDir);

        // from main/resources/logbroker.conf
        assertEquals("/taxi/consumers/testing/test-service-consumer", args.logbrokerConsumer);

        // from main/resources/logbroker-testing.conf
        assertEquals("/taxi/taxi-test-api-taxi-protocol-stats-surge-notify", args.subscriptionsTopic);

        // from main/resources/logbroker.conf
        assertEquals("/taxi/pins/testing/pin-storage", args.pinsTopic);

        // not found
        assertEquals("/taxi/taxi-test-order-offers-log", args.offersTopic);

        // from main/resources/services.conf
        assertEquals("superapp-misc.taxi.tst.yandex.net", args.services.get("superapp-misc"));

        // from main/resources/yt.conf
        assertEquals("//home/taxi/testing/replica/mongo/struct/corp/corp_clients",
                args.config.getString("yt.replica.corpClients"));
    }

    @Test
    void testFlinkJobConfig() {
        var args = new TestArgs(Environment.TESTING);
        Map<String, String> jobConfiguration = args.getJobConfiguration().toMap();
        assertEquals("EventTime", jobConfiguration.get("pipeline.time-characteristic"));
        assertEquals("false", jobConfiguration.get("pipeline.auto-generate-uids"));
    }
}
