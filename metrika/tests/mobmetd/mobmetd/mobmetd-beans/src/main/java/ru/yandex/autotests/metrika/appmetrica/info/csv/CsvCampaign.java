package ru.yandex.autotests.metrika.appmetrica.info.csv;

import org.apache.commons.lang3.builder.ToStringBuilder;
import ru.yandex.autotests.metrika.appmetrica.utils.BeanUtils;

import java.util.Date;
import java.util.List;

import static org.apache.commons.lang3.builder.ToStringStyle.SHORT_PREFIX_STYLE;

/**
 * @author dancingelf
 */
public class CsvCampaign {

    private final String trackingId;
    private final String name;
    private final Long appKey;
    private final Date createTime;

    public CsvCampaign(String trackingId, String name, Long appKey, Date createTime) {
        this.trackingId = trackingId;
        this.name = name;
        this.appKey = appKey;
        this.createTime = createTime;
    }

    public CsvCampaign(List<String> row) {
        this(row.get(0), row.get(1), Long.valueOf(row.get(2)),
                BeanUtils.parseIsoDtfWithSpace(row.get(3)));
    }

    public String getTrackingId() {
        return trackingId;
    }

    public String getName() {
        return name;
    }

    public Long getAppKey() {
        return appKey;
    }

    public Date getCreateTime() {
        return createTime;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this, SHORT_PREFIX_STYLE);
    }
}
