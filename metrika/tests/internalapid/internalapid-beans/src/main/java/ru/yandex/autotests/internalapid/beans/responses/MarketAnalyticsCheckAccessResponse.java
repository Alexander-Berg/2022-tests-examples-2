package ru.yandex.autotests.internalapid.beans.responses;

import java.util.List;

public class MarketAnalyticsCheckAccessResponse {
    private int counterId;
    private List<Long> uids;

    public MarketAnalyticsCheckAccessResponse() {
    }

    public MarketAnalyticsCheckAccessResponse(int counterId, List<Long> uids) {
        this.counterId = counterId;
        this.uids = uids;
    }

    public void setUids(List<Long> uids) {
        this.uids = uids;
    }

    public void setCounterId(int counterId) {
        this.counterId = counterId;
    }

    public List<Long> getUids() {
        return uids;
    }

    public int getCounterId() {
        return counterId;
    }
}
