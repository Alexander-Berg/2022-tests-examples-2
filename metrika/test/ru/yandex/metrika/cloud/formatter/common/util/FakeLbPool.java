package ru.yandex.metrika.cloud.formatter.common.util;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.function.Function;

import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.metrika.cloud.formatter.common.producers.LbProducerAsyncPool;
import ru.yandex.metrika.cloud.formatter.common.producers.ProducerAddress;
import ru.yandex.metrika.lb.serialization.BatchSerializer;

public class FakeLbPool implements LbProducerAsyncPool {
    private final ConcurrentMap<ProducerAddress, FakeLbProducer> cache = new ConcurrentHashMap<>();

    public ConcurrentMap<ProducerAddress, FakeLbProducer> getCache() {
        return cache;
    }

    public <T> List<T> readFlatData(BatchSerializer<T> serializer) {
        return cache.values().stream().flatMap(fakeLbProducer ->
                        fakeLbProducer.messages.stream().flatMap(message ->
                                serializer.deserialize(message.data()).stream()
                        )
                )
                .toList();
    }

    @Override
    public CompletableFuture<AsyncProducer> getAsync(String sourceId) {
        return getAsync(new ProducerAddress(sourceId));
    }

    @Override
    public CompletableFuture<AsyncProducer> getAsync(ProducerAddress address) {
        cache.putIfAbsent(address, new FakeLbProducer());
        return CompletableFuture.completedFuture(cache.get(address));
    }

    @Override
    public <T> CompletableFuture<T> runWithInvalidationOnFail(
            ProducerAddress address, Function<AsyncProducer, CompletableFuture<T>> action
    ) {
        return getAsync(address).thenCompose(action);
    }


}
