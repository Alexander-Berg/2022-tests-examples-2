package ru.yandex.yt.ytclient.proxy;

import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ScheduledExecutorService;

import ru.yandex.inside.yt.kosher.common.GUID;
import ru.yandex.inside.yt.kosher.common.YtTimestamp;

import static org.mockito.Mockito.mock;

public class ApiServiceTransactionMock extends ApiServiceTransaction {

    ApiServiceTransactionMock(
            ApiServiceClientImpl client, GUID  id, YtTimestamp startTimestamp,
            boolean ping, boolean pingAncestors, boolean sticky,
            Duration pingPeriod, ScheduledExecutorService executor
    ) {
        super(client, id, startTimestamp, ping, pingAncestors, sticky, pingPeriod, executor);
    }

    public static ApiServiceTransactionMock build(ApiServiceClientImpl client) {
        return new ApiServiceTransactionMock(
                client, GUID.create(), mock(YtTimestamp.class),
                false, false, false,
                Duration.ZERO, null
        );
    }

    @Override
    public CompletableFuture<Void> modifyRows(AbstractModifyRowsRequest request) {
        return CompletableFuture.runAsync(() -> {});
    }

    public CompletableFuture<Void> modifyRows(ModifyRowsRequest request) {
        return CompletableFuture.runAsync(() -> {});
    }

    @Override
    public CompletableFuture<Void> commit() {
        return CompletableFuture.runAsync(() -> {});
    }

    @Override
    public CompletableFuture<Void> abort() {
        return CompletableFuture.runAsync(() -> {});
    }

    @Override
    public void close() {
    }
}
