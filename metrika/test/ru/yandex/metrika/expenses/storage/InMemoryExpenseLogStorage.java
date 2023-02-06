package ru.yandex.metrika.expenses.storage;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.google.common.collect.LinkedHashMultiset;

public class InMemoryExpenseLogStorage implements ExpenseLogStorage {

    private final List<ExpenseLogRow> data = new ArrayList<>();
    private final Set<List<ExpenseLogRow>> deduplicationState = new HashSet<>();

    @Override
    public void insert(List<ExpenseLogRow> rows) {
        if (deduplicationState.add(rows)) {
            data.addAll(rows);
        }
    }

    public Collection<ExpenseLogRow> getData() {
        return LinkedHashMultiset.create(data);
    }
}
