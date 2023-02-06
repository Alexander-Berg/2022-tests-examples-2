package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import ru.yandex.metrika.monitoring.MonNotification;
import ru.yandex.metrika.monitoring.logbroker.LogbrokerStatusChange;

public class TestHelper {
    private final Set<Long> generatedCId;
    private int domainNumber;

    public TestHelper() {
        generatedCId = new HashSet<>();
    }

    public long getRndCounterId(int digits) {

        long min = (long) Math.pow(10, digits - 1);
        long result = 0;
        while (result == 0 || generatedCId.contains(result)) {
            result = ThreadLocalRandom.current().nextLong(min, min * 10);
        }
        generatedCId.add(result);
        return result;
    }

    public String getNextDomain() {
        String result = String.format("domain%08d", domainNumber);
        domainNumber += 1;
        return result;
    }

    public <T> Set<T> getRandomSubset(Collection<T> mainSet, int size) {
        return IntStream
                .range(0, size)
                .mapToObj(value -> {
                    int itemIdx = ThreadLocalRandom.current().nextInt(mainSet.size());
                    int curIdx = 0;
                    for (T item : mainSet) {
                        if (curIdx == itemIdx) {
                            return item;
                        }
                        curIdx += 1;
                    }
                    return null;
                })
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());
    }

    public List<LogbrokerStatusChange> generateStatusChanges(Collection<String> domains, int count) {
        String[] domainsArr = domains.toArray(new String[0]);
        long now = System.currentTimeMillis();
        return IntStream
                .range(0, count)
                .mapToObj(idx -> {
                    String domain = domainsArr[ThreadLocalRandom.current().nextInt(domainsArr.length)];
                    int httpCode = 200;
                    if (ThreadLocalRandom.current().nextBoolean()) {
                        httpCode = 500;
                    }
                    return new LogbrokerStatusChange(
                            Set.of("metrika"),
                            now + idx,
                            0,
                            0,
                            httpCode,
                            domain,
                            200,
                            0
                    );
                })
                .collect(Collectors.toList());
    }

    public boolean comparedStates(List<MonNotification> oldNotifications, List<MonNotification> newNotifications) {
        if (oldNotifications.size() != newNotifications.size()) {
            return false;
        }
        MonNotification[] oldArray = oldNotifications.toArray(new MonNotification[0]);
        MonNotification[] newArray = newNotifications.toArray(new MonNotification[0]);

        final boolean[] result = {true};
        IntStream.range(0, newNotifications.size()).forEach(idx -> {
            result[0] = result[0] && (oldArray[idx].toString().equals(newArray[idx].toString()));
        });
        return result[0];
    }
}
