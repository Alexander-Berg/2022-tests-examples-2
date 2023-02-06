package ru.yandex.metrika.expenses.storage;

import java.time.LocalDate;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.TreeMap;
import java.util.stream.Collectors;

import org.apache.commons.lang3.tuple.Pair;

import ru.yandex.metrika.expenses.connectors.AdsConnectorsStateStorage;
import ru.yandex.metrika.expenses.connectors.AdsExpensesYdbKey;
import ru.yandex.metrika.expenses.connectors.AdsExpensesYdbRow;

import static java.util.Collections.emptyIterator;

public class AdsConnectorsStateStorageInMemory<T extends AdsExpensesYdbRow> implements AdsConnectorsStateStorage<T> {

    // to be able to look up by key prefix (`CustomerId`,`Date`) store data by Pair<Key.CustomerId,Key.Date> -> Map<Key,Row>
    private final TreeMap<Pair<Long, LocalDate>, Map<AdsExpensesYdbKey, AdsExpensesYdbRow>> byKeyPrefix = new TreeMap<>();

    @Override
    public Iterator<T> load(long customerId, LocalDate date, boolean deleted) {
        Map<AdsExpensesYdbKey, AdsExpensesYdbRow> key2row = byKeyPrefix.get(Pair.of(customerId, date));
        if (key2row == null) {
            return emptyIterator();
        }

        Iterator<AdsExpensesYdbRow> it = key2row.values().iterator();
        return new Iterator<>() {
            private AdsExpensesYdbRow next;

            @Override
            public boolean hasNext() {
                if (next != null) return true;
                while (it.hasNext()) {
                    AdsExpensesYdbRow row = it.next();
                    if (deleted ^ !row.isDeleted()) {
                        next = row;
                        return true;
                    }
                }
                return false;
            }

            @Override
            public T next() {
                if (!hasNext()) throw new NoSuchElementException();
                AdsExpensesYdbRow ret = next;
                next = null;
                return (T) ret;
            }
        };
    }

    @Override
    public void save(Collection<T> rows) {
        for (T row : rows) {
            Map<AdsExpensesYdbKey, AdsExpensesYdbRow> key2row =
                    byKeyPrefix.computeIfAbsent(Pair.of(row.getCustomerAccountId(), row.getDate()), k -> new HashMap<>());
            key2row.put(row.getId(), row);
        }
    }

    @Override
    public Iterator<T> readTable(
            long customerId,
            LocalDate fromDateInclusive
    ) {
        Pair<Long, LocalDate> fromKey = Pair.of(customerId, fromDateInclusive);
        return byKeyPrefix.tailMap(fromKey).values()
                .stream()
                .flatMap(m -> m.values().stream())
                .sorted(Comparator.comparing(AdsExpensesYdbRow::getId))
                .map(r -> (T) r)
                .iterator();
    }

    @Override
    public String getTable() {
        throw new UnsupportedOperationException();
    }

    public List<T> getAllRows() {
        return byKeyPrefix.values()
                .stream()
                .flatMap(map -> map.values().stream())
                .map(r -> (T) r)
                .collect(Collectors.toList());
    }
}
