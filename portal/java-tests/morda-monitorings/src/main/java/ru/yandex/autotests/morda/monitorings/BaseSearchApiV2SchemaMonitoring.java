package ru.yandex.autotests.morda.monitorings;

import org.junit.Test;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.SearchApiVersion;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetric;

/**
 * User: asamar
 * Date: 05.10.16
 */
public abstract class BaseSearchApiV2SchemaMonitoring extends BaseSearchApiSchemaMonitoring {

    public BaseSearchApiV2SchemaMonitoring(SearchApiRequestData requestData) {
        super(requestData);
    }

    @Override
    protected SearchApiVersion getVersion() {
        return SearchApiVersion.v2;
    }

    @Override
    @Test
    @GolemEvent("apisearch_v2_schema")
    @GraphiteMetric("schema")
    public void schema() {
        super.schema();
    }
}
