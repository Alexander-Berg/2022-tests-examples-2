package ru.yandex.autotests.advapi.data.common;

public class Campaign {

    // clicks
    public static final Campaign YNDX_TAXI = new Campaign(1015L, 51670660L, "2019-09-01", "2019-09-06");
    // video
    public static final Campaign YNDX_MARKET_W = new Campaign(703L, 35361660L, "2019-07-03", "2019-07-09");

    private Campaign(long id, long goalId, String date1, String date2) {
        this.id = id;
        this.goalId = goalId;
        this.date1 = date1;
        this.date2 = date2;
    }

    public final long id;
    public final long goalId;
    public final String date1;
    public final String date2;
}
