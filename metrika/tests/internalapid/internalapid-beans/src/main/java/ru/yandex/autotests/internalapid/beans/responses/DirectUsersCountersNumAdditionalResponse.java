package ru.yandex.autotests.internalapid.beans.responses;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class DirectUsersCountersNumAdditionalResponse {
    private List<DirectUserCountersNumResponse> users;
    private boolean hasMoreCounters;

    public DirectUsersCountersNumAdditionalResponse(List<DirectUserCountersNumResponse> users,
                                                    boolean hasMoreCounters) {
        this.users = users;
        this.hasMoreCounters = hasMoreCounters;
    }

    public List<DirectUserCountersNumResponse> getUsers() {
        return users;
    }

    public boolean isHasMoreCounters() {
        return hasMoreCounters;
    }

    public static DirectUsersCountersNumAdditionalResponse parseFrom(Object obj) {
        Map<?, ?> map = (Map<?, ?>) obj;
        boolean hasMoreCounters = ((Boolean) map.get("has_more_counters"));
        List<?> rawUsers = (List) map.get("users");
        List<DirectUserCountersNumResponse> users =
                rawUsers.stream().map(DirectUserCountersNumResponse::parseFrom).collect(Collectors.toList());
        return new DirectUsersCountersNumAdditionalResponse(users, hasMoreCounters);
    }

}
