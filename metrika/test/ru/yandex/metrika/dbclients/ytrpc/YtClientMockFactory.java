package ru.yandex.metrika.dbclients.ytrpc;

import java.util.Collections;
import java.util.concurrent.CompletableFuture;

import org.jetbrains.annotations.NotNull;

import ru.yandex.yt.ytclient.proxy.ApiServiceTransaction;
import ru.yandex.yt.ytclient.proxy.ApiServiceTransactionMock;
import ru.yandex.yt.ytclient.proxy.ApiServiceTransactionOptions;
import ru.yandex.yt.ytclient.proxy.YtClient;
import ru.yandex.yt.ytclient.wire.UnversionedRowset;

import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class YtClientMockFactory {

    public static YtClient apiClientWithTransaction() {
        YtClient apiClient = apiClient();
        ApiServiceTransactionMock transactionMock = ApiServiceTransactionMock.build(apiClient);
        CompletableFuture<ApiServiceTransaction> transactionFuture = CompletableFuture.supplyAsync(() -> transactionMock);
        when(apiClient.startTransaction(any(ApiServiceTransactionOptions.class))).thenReturn(transactionFuture);
        return apiClient;
    }

    @NotNull
    private static YtClient apiClient() {
        UnversionedRowset unversionedRowset = mock(UnversionedRowset.class);
        when(unversionedRowset.getRows()).thenReturn(Collections.emptyList());
        CompletableFuture<UnversionedRowset> lookupResult = CompletableFuture.supplyAsync(() -> unversionedRowset);
        YtClient client = mock(YtClient.class);
        when(client.lookupRows(any())).thenReturn(lookupResult);
        when(client.selectRows(anyString())).thenReturn(lookupResult);
        return client;
    }
}
