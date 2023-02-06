package ru.yandex.autotests.advapi.parameters;

public enum CampaignsSort {
    name("c.name"),
    advertiser("a.name"),
    start("date_start"),
    end("date_end"),
    days_left("days_left"),
    impressions("renders_from_start"),
    conversions("goal_reaches_from_start"),
    conversion("conversion"),
    cost("avg_cpa_from_start");

    private String column;

    CampaignsSort(String column) {
        this.column = column;
    }

    public String getColumn() {
        return column;
    }
}
