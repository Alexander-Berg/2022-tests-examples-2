package ru.yandex.metrika.dbclients.ytrpc;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;

import ru.yandex.yt.ytclient.proxy.ApiServiceClient;
import ru.yandex.yt.ytclient.proxy.ApiServiceTransaction;

import static ru.yandex.metrika.dbclients.ytrpc.YtTransactionUtils.defaultTransactionOptions;

public class CountingYtTransactionalExecutor extends YtTransactionalExecutor {

    private AtomicInteger currentTransactionCounter = new AtomicInteger();
    private AtomicInteger newTransactionCounter = new AtomicInteger();

    public CountingYtTransactionalExecutor(ApiServiceClient apiServiceClient) {
        super(apiServiceClient, defaultTransactionOptions());
    }

    @Override
    protected void doInCurrentTransaction(ApiServiceTransaction transaction, Function<ApiServiceTransaction, CompletableFuture<Void>> function) {
        currentTransactionCounter.incrementAndGet();
        super.doInCurrentTransaction(transaction, function);
    }

    @Override
    protected void doInNewTransaction(ApiServiceTransaction transaction, Function<ApiServiceTransaction, CompletableFuture<Void>> function) {
        newTransactionCounter.incrementAndGet();
        super.doInNewTransaction(transaction, function);
    }

    public Integer getCurrentTransactionCounter() {
        return currentTransactionCounter.get();
    }

    public Integer getNewTransactionCounter() {
        return newTransactionCounter.get();
    }
}
