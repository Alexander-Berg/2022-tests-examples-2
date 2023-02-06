package ru.yandex.autotests.internalapid.beans.responses;

import java.util.Map;
import java.util.Objects;

public class DirectUpdatedUserCountersNumResponse {
    private long owner;
    private String lastUpdateTime;
    private int countersNum;

    public DirectUpdatedUserCountersNumResponse(long owner, int countersNum, String lastUpdateTime) {
        this.owner = owner;
        this.countersNum = countersNum;
        this.lastUpdateTime = lastUpdateTime;
    }

    public DirectUpdatedUserCountersNumResponse() {
    }

    public long getOwner() {
        return owner;
    }

    public DirectUpdatedUserCountersNumResponse withOwner(long owner) {
        this.owner = owner;
        return this;
    }

    public int getCountersNum() {
        return countersNum;
    }

    public DirectUpdatedUserCountersNumResponse withCountersNum(int countersNum) {
        this.countersNum = countersNum;
        return this;
    }

    public String getLastUpdateTime() {
        return lastUpdateTime;
    }

    public DirectUpdatedUserCountersNumResponse withLastUpdateTime(String lastUpdateTime) {
        this.lastUpdateTime = lastUpdateTime;
        return this;
    }

    public static DirectUpdatedUserCountersNumResponse parseFrom(Object obj) {
        Map<?, ?> map = (Map<?, ?>) obj;
        long owner = ((Number) map.get("owner")).longValue();
        int countersNum = ((Number) map.get("counters_cnt")).intValue();
        String lastUpdateTime = ((String) map.get("last_update_time"));
        return new DirectUpdatedUserCountersNumResponse(owner, countersNum, lastUpdateTime);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DirectUpdatedUserCountersNumResponse that = (DirectUpdatedUserCountersNumResponse) o;
        return owner == that.owner &&
                countersNum == that.countersNum &&
                Objects.equals(lastUpdateTime, that.lastUpdateTime);
    }

    @Override
    public int hashCode() {
        return Objects.hash(owner, lastUpdateTime, countersNum);
    }

    @Override
    public String toString() {
        return "{" +
                "owner=" + owner +
                ", lastUpdateTime='" + lastUpdateTime + '\'' +
                ", countersNum=" + countersNum +
                '}';
    }
}
