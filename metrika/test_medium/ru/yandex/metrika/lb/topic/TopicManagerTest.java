package ru.yandex.metrika.lb.topic;

import java.time.Duration;
import java.time.Instant;
import java.util.List;

import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

public class TopicManagerTest {

    private static String endpoint;
    private static String database;

    private TopicManager topicManager;
    private String topicPath;

    @BeforeClass
    public static void initClass() {
        endpoint = System.getenv("YDB_ENDPOINT");
        if (endpoint == null) {
            endpoint = "localhost:2136";
        }

        database = System.getenv("YDB_DATABASE");
        if (database == null) {
            database = "local";
        }
    }

    @Before
    public void init() {
        String[] hostPort = endpoint.split(":");
        String host = hostPort[0];
        int port = Integer.parseInt(hostPort[1]);

        topicManager = new TopicManager();
        topicManager.setHost(host);
        topicManager.setPort(port);
        topicManager.init();

        topicPath = "/" + database + "/topic";
    }

    @Test
    public void testCreateTopicMinimal() {
        topicManager.createTopic(CreateTopicParams.builder(topicPath).build());
        TopicInfo topicInfo = topicManager.describeTopic(topicPath);
        Assert.assertEquals(topicPath, topicInfo.path());
    }

    @Test
    public void testCreateTopicWithSettings() {
        topicManager.createTopic(CreateTopicParams.builder(topicPath)
                .withPartitioningSettings(PartitioningSettings.builder()
                        .withMinActivePartitions(2)
                        .build()
                )
                .withRetentionPeriod(Duration.ofHours(24))
                .withSupportedCodecs(List.of(Codec.RAW, Codec.ZSTD))
                .withConsumers(List.of(
                        ConsumerInfo.builder("consumer1")
                                .withImportant(true)
                                .withReadFrom(Instant.EPOCH)
                                .withSupportedCodecs(List.of(Codec.RAW, Codec.ZSTD, Codec.LZOP))
                                .build(),
                        ConsumerInfo.builder("consumer2")
                                .withImportant(false)
                                .withReadFrom(Instant.parse("2022-06-05T04:03:02.00Z"))
                                .withSupportedCodecs(List.of(Codec.RAW, Codec.ZSTD))
                                .build()
                ))
                .build()
        );

        TopicInfo topicInfo = topicManager.describeTopic(topicPath);
        Assert.assertEquals(topicPath, topicInfo.path());
        Assert.assertEquals(2, topicInfo.partitioningSettings().minActivePartitions());
        Assert.assertEquals(Duration.ofHours(24), topicInfo.retentionPeriod());
        Assert.assertThat(topicInfo.supportedCodecs(), Matchers.containsInAnyOrder(Codec.RAW, Codec.ZSTD));
        Assert.assertThat(topicInfo.consumers(), Matchers.hasSize(2));

        ConsumerInfo consumer1 = topicInfo.consumers().stream().filter(c -> c.name().equals("consumer1")).findAny().orElseThrow();
        Assert.assertTrue(consumer1.important());
        Assert.assertEquals(Instant.EPOCH, consumer1.readFrom());
        Assert.assertThat(consumer1.supportedCodecs(), Matchers.containsInAnyOrder(Codec.RAW, Codec.ZSTD, Codec.LZOP));

        ConsumerInfo consumer2 = topicInfo.consumers().stream().filter(c -> c.name().equals("consumer2")).findAny().orElseThrow();
        Assert.assertFalse(consumer2.important());
        Assert.assertEquals(Instant.parse("2022-06-05T04:03:02.00Z"), consumer2.readFrom());
        Assert.assertThat(consumer2.supportedCodecs(), Matchers.containsInAnyOrder(Codec.RAW, Codec.ZSTD));
    }

    @Test
    public void testAlterTopic() {
        topicManager.createTopic(CreateTopicParams.builder(topicPath)
                .withConsumers(List.of(
                        ConsumerInfo.builder("consumer1")
                                .build(),
                        ConsumerInfo.builder("consumer2")
                                .build()
                ))
                .build()
        );

        topicManager.alterTopic(AlterTopicParams.builder(topicPath)
                .withAlterPartitioningSettings(AlterPartitioningSettingsParams.builder()
                        .withSetMinActivePartitions(2L)
                        .build()
                )
                .withSetRetentionPeriod(Duration.ofHours(24))
                .withSetSupportedCodecs(List.of(Codec.RAW, Codec.ZSTD))
                .withAddConsumers(List.of(
                        ConsumerInfo.builder("consumer3")
                                .withImportant(false)
                                .withReadFrom(Instant.EPOCH)
                                .withSupportedCodecs(List.of(Codec.RAW, Codec.ZSTD))
                                .build()))
                .withDropConsumers(List.of("consumer1"))
                .withAlterConsumers(List.of(
                        AlterConsumerParams.builder("consumer2")
                                .withSetImportant(true)
                                .withSetReadFrom(Instant.parse("2022-06-05T04:03:02.00Z"))
                                .withSetSupportedCodecs(List.of(Codec.RAW, Codec.ZSTD, Codec.LZOP))
                                .build()
                ))
                .build()
        );

        TopicInfo topicInfo = topicManager.describeTopic(topicPath);
        Assert.assertEquals(topicPath, topicInfo.path());
        Assert.assertEquals(2, topicInfo.partitioningSettings().minActivePartitions());
        Assert.assertEquals(Duration.ofHours(24), topicInfo.retentionPeriod());
        Assert.assertThat(topicInfo.supportedCodecs(), Matchers.containsInAnyOrder(Codec.RAW, Codec.ZSTD));
        Assert.assertThat(topicInfo.consumers(), Matchers.hasSize(2));

        ConsumerInfo consumer2 = topicInfo.consumers().stream().filter(c -> c.name().equals("consumer2")).findAny().orElseThrow();
        Assert.assertTrue(consumer2.important());
        Assert.assertEquals(Instant.parse("2022-06-05T04:03:02.00Z"), consumer2.readFrom());
        Assert.assertThat(consumer2.supportedCodecs(), Matchers.containsInAnyOrder(Codec.RAW, Codec.ZSTD, Codec.LZOP));

        ConsumerInfo consumer3 = topicInfo.consumers().stream().filter(c -> c.name().equals("consumer3")).findAny().orElseThrow();
        Assert.assertFalse(consumer3.important());
        Assert.assertEquals(Instant.EPOCH, consumer3.readFrom());
        Assert.assertThat(consumer3.supportedCodecs(), Matchers.containsInAnyOrder(Codec.RAW, Codec.ZSTD));
    }

    @Test
    public void testDropTopic() {
        topicManager.createTopic(CreateTopicParams.builder(topicPath).build());
        topicManager.dropTopic(topicPath);
    }

    @After
    public void clean() {
        try {
            topicManager.dropTopic(topicPath);
        } catch (Exception ignored) {
        }
    }
}
