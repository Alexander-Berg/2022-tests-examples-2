package ru.yandex.metrika.cdp.api;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import org.apache.commons.lang3.tuple.MutableTriple;

import ru.yandex.metrika.cdp.dto.schema.ListType;
import ru.yandex.metrika.cdp.validation.ListsChecker;

public class InMemoryListsChecker implements ListsChecker {

    private final Map<ListKey, Set<String>> listToItemsMap = new ConcurrentHashMap<>();

    @Override
    public boolean isListItemExists(int counterId, ListType listType, String listName, String itemName) {
        return listToItemsMap.computeIfAbsent(new ListKey(counterId, listType, listName), unused -> new HashSet<>()).contains(itemName);
    }

    @Override
    public boolean isListExists(int counterId, ListType listType, String listName) {
        return listToItemsMap.containsKey(new ListKey(counterId, listType, listName));
    }

    public void add(int counterId, ListType listType, String listName, String... itemNames) {
        listToItemsMap.computeIfAbsent(new ListKey(counterId, listType, listName), unused -> new HashSet<>()).addAll(Arrays.asList(itemNames));
    }

    public void remove(int counterId, ListType listType, String listName) {
        listToItemsMap.remove(new ListKey(counterId, listType, listName));
    }

    private static class ListKey extends MutableTriple<Integer, ListType, String> {

        public ListKey(Integer left, ListType middle, String right) {
            super(left, middle, right);
        }
    }
}
