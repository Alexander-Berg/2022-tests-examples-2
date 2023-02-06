package ru.yandex.metrika.mobmet.crash.decoder.service.library;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

import ru.yandex.metrika.mobmet.crash.library.LibraryPredicate;

public class DummyLibraryService extends LibraryPredicatesService {

    private Map<Integer, Predicate<String>> predicates;

    public DummyLibraryService() {
        this(Collections.emptyList());
    }

    public DummyLibraryService(List<LibraryPredicate> containsStringList) {
        super(null);
        predicates = buildPredicates(containsStringList);
    }

    public Map<Integer, Predicate<String>> androidPredicates() {
        return predicates;
    }

    public Map<Integer, Predicate<String>> applePredicates() {
        return predicates;
    }
}
