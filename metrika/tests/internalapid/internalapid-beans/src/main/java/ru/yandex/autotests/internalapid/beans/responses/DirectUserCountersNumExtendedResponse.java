package ru.yandex.autotests.internalapid.beans.responses;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import ru.yandex.metrika.api.management.client.external.CounterPermission;

public class DirectUserCountersNumExtendedResponse {
    private long owner;
    private int countersNum;
    private Set<ExtendedCounterInfo> counters;

    public DirectUserCountersNumExtendedResponse(long owner, int countersNum, Set<ExtendedCounterInfo> counters) {
        this.owner = owner;
        this.countersNum = countersNum;
        this.counters = counters;
    }

    public static DirectUserCountersNumExtendedResponse parseFrom(Object obj) {
        Map<?, ?> map = (Map<?, ?>) obj;
        long owner = ((Number) map.get("owner")).longValue();
        int countersNum = ((Number) map.get("counters_cnt")).intValue();
        Set<ExtendedCounterInfo> counters = ((List<?>) map.get("counters")).stream().map(ExtendedCounterInfo::parseFrom).collect(Collectors.toSet());
        return new DirectUserCountersNumExtendedResponse(owner, countersNum, counters);
    }

    public long getOwner() {
        return owner;
    }

    public void setOwner(long owner) {
        this.owner = owner;
    }

    public int getCountersNum() {
        return countersNum;
    }

    public void setCountersNum(int countersNum) {
        this.countersNum = countersNum;
    }

    public Set<ExtendedCounterInfo> getCounters() {
        return counters;
    }

    public void setCounters(Set<ExtendedCounterInfo> counters) {
        this.counters = counters;
    }

    public static class ExtendedCounterInfo {
        private int id;
        private String name;
        private String sitePath;
        private CounterPermission counterPermission;
        private boolean ecommerce;

        public ExtendedCounterInfo(int id, String name, String sitePath, CounterPermission counterPermission, boolean ecommerce) {
            this.id = id;
            this.name = name;
            this.sitePath = sitePath;
            this.counterPermission = counterPermission;
            this.ecommerce = ecommerce;
        }

        public static ExtendedCounterInfo parseFrom(Object obj) {
            Map<?, ?> map = (Map<?, ?>) obj;
            int counterId = ((Number) map.get("id")).intValue();
            String name = (String) map.get("name");
            String sitePath = (String) map.get("site_path");
            CounterPermission counterPermission = CounterPermission.fromValue((String) map.get("counter_permission"));
            boolean ecommerce = (Boolean) map.get("ecommerce");
            return new ExtendedCounterInfo(counterId, name, sitePath, counterPermission, ecommerce);
        }

        public int getId() {
            return id;
        }

        public void setId(int id) {
            this.id = id;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getSitePath() {
            return sitePath;
        }

        public void setSitePath(String sitePath) {
            this.sitePath = sitePath;
        }

        public CounterPermission getCounterPermission() {
            return counterPermission;
        }

        public void setCounterPermission(CounterPermission counterPermission) {
            this.counterPermission = counterPermission;
        }

        public boolean isEcommerce() {
            return ecommerce;
        }

        public void setEcommerce(boolean ecommerce) {
            this.ecommerce = ecommerce;
        }
    }
}
