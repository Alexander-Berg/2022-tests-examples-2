package ru.yandex.metrika.restream.sharder.sharding;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.apache.logging.log4j.Level;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.impl.YtConfiguration;
import ru.yandex.metrika.dbclients.yt.YtDatabase;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.log.Log4jSetup;

import static ru.yandex.metrika.restream.sharder.sharding.ShardingTestUtils.sr;

public class YtCounterSharderProviderTest {

    static {
        Log4jSetup.basicArcadiaSetup(Level.DEBUG);
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.inside.yt.kosher.impl.common.http.HttpUtils");
    }

    @Test
    @Ignore("local only")
    public void test() {
        var token = XmlPropertyConfigurer.getTextFromVault("sec-01e9tsb0485zrewv4jq0kg68c4/token"); // robot-metrika-java-t

        var ytDatabase = new YtDatabase(List.of("hahn.yt.yandex.net", "arnold.yt.yandex.net"), token);
        ytDatabase.setSimpleCommandsRetries(2);
        ytDatabase.afterPropertiesSet();

        var locke = Yt.builder(
                YtConfiguration.builder()
                        .withApiHost("locke.yt.yandex.net")
                        .withToken(token)
                        .withSimpleCommandsRetries(2)
                        .withHeavyCommandsRetries(1)
                        .build()
        ).http().build();


        ShardingInfoProvider shardingInfoProvider = () -> List.of(
                new CounterShardingInfo(1, 10, List.of(sr(1, 1), sr(2, 1))),
                new CounterShardingInfo(2, 11, List.of(sr(3, 1))),
                new CounterShardingInfo(3, 3, List.of(sr(4, 2), sr(5, 1))),
                new CounterShardingInfo(4, 58, List.of(sr(6, 1))),
                new CounterShardingInfo(5, 34, List.of(sr(7, 1), sr(8, 1), sr(9, 100500))),
                new CounterShardingInfo(6, 5, List.of(sr(10, 1))),
                new CounterShardingInfo(7, 33, List.of(sr(11, 1), sr(12, 1))),
                new CounterShardingInfo(8, 20, List.of(sr(13, 1), sr(14, 1), sr(15, 1), sr(16, 1), sr(17, 1)))
        );

        var futures = IntStream.range(0, 1).mapToObj(i ->
                CompletableFuture.runAsync(() -> {
                    var shardingTableBuilder = new ShardingTableBuilder(4, shardingInfoProvider);
                    var ytSegmentSharderProvider = new YtCounterSharderProvider(
                            ytDatabase, locke, shardingTableBuilder,
                            "//home/metrika/restream/development/sharding_tables",
                            "//home/metrika/restream/development/sharding_build"
                    );
                    ytSegmentSharderProvider.setRebuildTimeoutMinutes(10);
                    ytSegmentSharderProvider.afterPropertiesSet();

                    var segmentSharder = ytSegmentSharderProvider.get();
                    System.out.println(segmentSharder);

                    ytSegmentSharderProvider.updateSharder();
                    segmentSharder = ytSegmentSharderProvider.get();
                    System.out.println(segmentSharder);
                }))
                .collect(Collectors.toList());
        F.sequence(futures).join();
    }


}
