package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.Collection;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import ru.yandex.metrika.schedulerd.cron.task.monitoringd.DomainCountersDao;

public class DomainCountersDaoMock extends DomainCountersDao {
    private final Map<String, Set<Integer>> domainCountersMap;

    public DomainCountersDaoMock(Map<String, Set<Integer>> domainCountersMap) {
        super();
        this.domainCountersMap = domainCountersMap;
    }

    @Override
    public Map<String, Set<Integer>> getDomainToCountersMap(Collection<String> domains) {
        return domainCountersMap
                .entrySet()
                .stream()
                .filter(domainCounterEntrySet -> domains.contains(domainCounterEntrySet.getKey()))
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }
}
