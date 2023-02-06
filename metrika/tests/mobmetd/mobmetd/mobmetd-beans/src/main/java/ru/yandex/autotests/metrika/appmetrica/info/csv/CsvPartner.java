package ru.yandex.autotests.metrika.appmetrica.info.csv;

import org.apache.commons.lang3.builder.ToStringBuilder;

import java.util.List;

import static org.apache.commons.lang3.builder.ToStringStyle.SHORT_PREFIX_STYLE;

/**
 * @author dancingelf
 */
public class CsvPartner {

    private final Long id;
    private final String name;
    private final String website;

    public CsvPartner(Long id, String name, String website) {
        this.id = id;
        this.name = name;
        this.website = website;
    }

    public CsvPartner(List<String> row) {
        this(Long.valueOf(row.get(0)), row.get(1), row.get(2));
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getWebsite() {
        return website;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this, SHORT_PREFIX_STYLE);
    }
}
