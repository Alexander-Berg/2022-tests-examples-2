package ru.yandex.yt.ytclient.proxy;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.IntStream;

import ru.yandex.yt.ytclient.bus.DefaultBusConnector;
import ru.yandex.yt.ytclient.rpc.RpcCredentials;
import ru.yandex.yt.ytclient.rpc.RpcOptions;
import ru.yandex.yt.ytclient.tables.ColumnValueType;
import ru.yandex.yt.ytclient.tables.TableSchema;
import ru.yandex.yt.ytclient.wire.UnversionedRow;
import ru.yandex.yt.ytclient.wire.UnversionedRowset;
import ru.yandex.yt.ytclient.wire.UnversionedValue;

import static java.util.Collections.singletonList;
import static org.mockito.Mockito.mock;

public class YtClientMock extends YtClient {

    private static final Pattern pattern = Pattern.compile("value where value > (\\d+)");
    private int tableSize;
    private int queryLimit;

    public YtClientMock() {
        super(new DefaultBusConnector(),
                "fake",
                new RpcCredentials(),
                new RpcOptions()
        );
    }

    public static YtClient getInstance(int queryLimit, int tableSize) {
        YtClientMock ytClientMock = new YtClientMock();
        ytClientMock.tableSize = tableSize;
        ytClientMock.queryLimit = queryLimit;
        return ytClientMock;
    }

    @Override
    public CompletableFuture<UnversionedRowset> selectRows(String query) {
        Matcher matcher = pattern.matcher(query);
        if (matcher.matches() && matcher.groupCount() > 0) {
            int i = Integer.valueOf(matcher.group(1));
            return getUnversionedRowsetCompletableFuture(i);
        }
        return null;
    }

    private CompletableFuture<UnversionedRowset> getUnversionedRowsetCompletableFuture(int i) {
        return CompletableFuture.supplyAsync(() -> {
            List<UnversionedRow> rows = new ArrayList<>();
            int upperBound = Math.min(i + queryLimit, tableSize);
            IntStream.rangeClosed(i + 1, upperBound).forEachOrdered(x -> rows.add(paramAsUnversionedRow(x)));
            return new UnversionedRowset(mock(TableSchema.class), rows);
        });
    }

    private UnversionedRow paramAsUnversionedRow(long value) {
        return new UnversionedRow(singletonList(
                new UnversionedValue(0, ColumnValueType.UINT64, false, value)));
    }
}
