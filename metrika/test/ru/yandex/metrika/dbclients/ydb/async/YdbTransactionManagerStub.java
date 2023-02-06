package ru.yandex.metrika.dbclients.ydb.async;

import java.util.concurrent.CompletableFuture;
import java.util.function.Function;

import com.yandex.ydb.core.Result;
import com.yandex.ydb.table.transaction.TransactionMode;
import com.yandex.ydb.table.transaction.TxControl;

public class YdbTransactionManagerStub implements YdbTransactionManager {

    @Override
    public <T> CompletableFuture<Result<T>> inTransaction(Function<QueryExecutionContext, CompletableFuture<T>> function, TransactionMode transactionMode) {
        return CompletableFuture.completedFuture(Result.success(function.apply(new QueryExecutionContext(TxControl.serializableRw())).join()));
    }

    @Override
    public long getTransactionTimeout() {
        return Long.MAX_VALUE;
    }
}
