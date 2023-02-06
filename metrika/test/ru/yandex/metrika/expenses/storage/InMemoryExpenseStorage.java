package ru.yandex.metrika.expenses.storage;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

import javax.annotation.Nullable;

public class InMemoryExpenseStorage implements ExpenseStorage {

    private final Map<ExpenseStorageRowId, ExpenseStorageRow> data = new HashMap<>();
    private final Map<Integer, Integer> uploadingOffsets = new HashMap<>();

    @Override
    public Map<ExpenseStorageRowId, ExpenseStorageRow> load(Collection<ExpenseStorageRowId> rowIds) {
        return rowIds.stream()
                .map(data::get)
                .filter(Objects::nonNull)
                .collect(Collectors.toMap(ExpenseStorageRow::id, Function.identity()));
    }

    @Override
    public Iterable<ExpenseStorageRow> load(
            int counterId,
            byte adsPlatform,
            long customerAccountId,
            @Nullable String provider,
            ExpenseStorageFilterOptions filterOptions,
            Collection<ExpenseStorageFilterItem> filter
    ) {
        Set<List<Object>> filterSet = filter.stream()
                .map(filterItem -> getFilterData(filterOptions, filterItem))
                .collect(Collectors.toSet());
        return data.values().stream()
                .filter(row -> row.counterId() == counterId &&
                        row.adsPlatform() == adsPlatform &&
                        row.customerAccountId() == customerAccountId &&
                        (provider == null || row.provider().equals(provider)) &&
                        filterSet.contains(getRowFilterData(filterOptions, row))
                )
                .collect(Collectors.toList());
    }

    @Override
    public void save(Collection<ExpenseStorageRow> rows, int uploadingId, int uploadingOffset) {
        rows.forEach(row -> data.put(row.id(), row));
        uploadingOffsets.put(uploadingId, uploadingOffset);
    }

    @Override
    public void remove(Collection<ExpenseStorageRowId> rowIds, int uploadingId, int uploadingOffset) {
        rowIds.forEach(data::remove);
        uploadingOffsets.put(uploadingId, uploadingOffset);
    }

    @Override
    public int getUploadingOffset(int uploadingId) {
        return uploadingOffsets.getOrDefault(uploadingId, 0);
    }

    public Collection<ExpenseStorageRow> getData() {
        return Set.copyOf(data.values());
    }

    private List<Object> getFilterData(ExpenseStorageFilterOptions filterOptions, ExpenseStorageFilterItem filterItem) {
        List<Object> result = new ArrayList<>();
        result.add(filterItem.getDate());
        if (filterOptions.isFilterUtmSource()) {
            result.add(filterItem.getUtmSource());
        }
        if (filterOptions.isFilterUtmMedium()) {
            result.add(filterItem.getUtmMedium());
        }
        if (filterOptions.isFilterUtmCampaign()) {
            result.add(filterItem.getUtmCampaign());
        }
        if (filterOptions.isFilterUtmTerm()) {
            result.add(filterItem.getUtmTerm());
        }
        if (filterOptions.isFilterUtmContent()) {
            result.add(filterItem.getUtmContent());
        }
        return result;
    }

    private List<Object> getRowFilterData(ExpenseStorageFilterOptions filterOptions, ExpenseStorageRow row) {
        List<Object> result = new ArrayList<>();
        result.add(row.date());
        if (filterOptions.isFilterUtmSource()) {
            result.add(row.utmSource());
        }
        if (filterOptions.isFilterUtmMedium()) {
            result.add(row.utmMedium());
        }
        if (filterOptions.isFilterUtmCampaign()) {
            result.add(row.utmCampaign());
        }
        if (filterOptions.isFilterUtmTerm()) {
            result.add(row.utmTerm());
        }
        if (filterOptions.isFilterUtmContent()) {
            result.add(row.utmContent());
        }
        return result;
    }
}
