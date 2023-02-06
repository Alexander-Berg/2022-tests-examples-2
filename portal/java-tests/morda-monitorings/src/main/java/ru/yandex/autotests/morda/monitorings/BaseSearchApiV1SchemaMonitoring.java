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
public abstract class BaseSearchApiV1SchemaMonitoring extends BaseSearchApiSchemaMonitoring {

    public BaseSearchApiV1SchemaMonitoring(SearchApiRequestData requestData) {
        super(requestData);
    }

    @Override
    protected SearchApiVersion getVersion() {
        return SearchApiVersion.v1;
    }

    @Override
    @Test
    @GolemEvent("apisearch_v1_schema")
    @GraphiteMetric("schema")
    public void schema() {
        super.schema();
    }
}
