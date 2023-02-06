package ru.yandex.metrika.cloud.formatter.config;

import java.util.concurrent.ExecutorService;
import java.util.function.Function;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.cloud.formatter.common.ExactlyOnceLbTransfer;
import ru.yandex.metrika.cloud.formatter.common.producers.LbProducerAsyncPool;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.lb.serialization.proto.GenericProtoSerializer;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqBatchSerializer;
import ru.yandex.metrika.util.concurrent.Pools;

import static ru.yandex.metrika.cloud.formatter.common.ShardAddress.defaultShardFunction;
import static ru.yandex.metrika.cloud.proto.FormattedVisitOuterClass.FormattedVisit;

@Configuration
@Import({CloudFormatterLbTestConfig.class})
public class CloudFormatterTransferTestConfig {

    @Bean
    public ProtoSerializer<FormattedVisit> formattedVisitSerializer() {
        return new GenericProtoSerializer<>(FormattedVisit.parser());
    }

    @Bean
    public ProtoSeqBatchSerializer<FormattedVisit> protoSeqFormattedVisitSerializer(
            ProtoSerializer<FormattedVisit> bannerGroupsProtoSerializer
    ) {
        return new ProtoSeqBatchSerializer<>(bannerGroupsProtoSerializer);
    }

    @Bean
    public ExecutorService formatterTestPool() {
        return Pools.newNamedFixedThreadPool(3, "formatter-test-pool");
    }


    @Bean
    public ExactlyOnceLbTransfer<FormattedVisit, FormattedVisit> visitFormatter(
            LbProducerAsyncPool producers,
            BatchSerializer<FormattedVisit> serializer,
            ExecutorService formatterTestPool
    ) {
        return new ExactlyOnceLbTransfer<>(
                producers, defaultShardFunction(),
                serializer, serializer,
                Function.identity(),
                formatterTestPool
        );
    }
}
