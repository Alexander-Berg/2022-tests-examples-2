package ru.yandex.autotests.internalapid.beans.responses;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

public class DirectUserCountersNumResponse {
    private long owner;
    private int countersNum;
    private Set<Integer> counters;

    public DirectUserCountersNumResponse(long owner, int countersNum, Set<Integer> counters) {
        this.owner = owner;
        this.countersNum = countersNum;
        this.counters = counters;
    }

    public DirectUserCountersNumResponse() {
    }

    public long getOwner() {
        return owner;
    }

    public DirectUserCountersNumResponse withOwner(long owner) {
        this.owner = owner;
        return this;
    }

    public int getCountersNum() {
        return countersNum;
    }

    public DirectUserCountersNumResponse withCountersNum(int countersNum) {
        this.countersNum = countersNum;
        return this;
    }

    public Set<Integer> getCounters() {
        return counters;
    }

    public DirectUserCountersNumResponse withCounters(Set<Integer> counters) {
        this.counters = counters;
        return this;
    }

    public static DirectUserCountersNumResponse parseFrom(Object obj) {
        Map<?, ?> map = (Map<?, ?>) obj;
        long owner = ((Number) map.get("owner")).longValue();
        int countersNum = ((Number) map.get("counters_cnt")).intValue();
        Set<Integer> counters = ((List<?>) map.get("counter_ids")).stream().map(it -> ((Number) it).intValue()).collect(Collectors.toSet());
        return new DirectUserCountersNumResponse(owner, countersNum, counters);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DirectUserCountersNumResponse that = (DirectUserCountersNumResponse) o;
        return owner == that.owner &&
                countersNum == that.countersNum &&
                Objects.equals(counters, that.counters);
    }

    @Override
    public int hashCode() {
        return Objects.hash(owner, countersNum, counters);
    }

    @Override
    public String toString() {
        return "{" +
                "owner=" + owner +
                ", countersNum=" + countersNum +
                ", counters=" + counters +
                '}';
    }
}
