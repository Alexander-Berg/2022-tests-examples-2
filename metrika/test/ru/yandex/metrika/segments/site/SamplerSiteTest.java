package ru.yandex.metrika.segments.site;

import java.util.Optional;

import org.apache.commons.math3.fraction.BigFraction;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Table;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.parts.FromBaseTable;
import ru.yandex.metrika.segments.core.schema.QueryEntity;

import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Created by orantius on 10.03.16.
 */
@Ignore("METRIQA-936")
public class SamplerSiteTest {

    @Test
    public void testSetSampleSize() {
        ApiUtilsConfig c = new ApiUtilsConfig();
        SamplerSite ss = new SamplerSite(c.getSampleSizes(), c.getGlobalSampleSizes(), c.getTuplesSampleSizes(), new RowsUniquesProvider() {
            @Override
            public RowsUniques getRowsUniques(QueryEntity entity, String startDate, String endDate, int counterId) {
                return new RowsUniques().setTableRows(1000_000L).setUniques(1000_000L);
            }
        });

        Query query = mock(Query.class);
        QueryContext qc = mock(QueryContext.class);
        when(qc.getIdByName(anyString())).thenReturn(new int[]{42});
        when(qc.isEnableSampling()).thenReturn(true);
        when(query.getQueryContext()).thenReturn(qc);
        Table table = new Table("table");
        when(query.getFromTable()).thenReturn(new FromBaseTable(table, table));
        when(query.getDimensionFilters()).thenReturn(Optional.empty());
        when(query.getMetricFilters()).thenReturn(Optional.empty());
        ss.setSampleSize(query, "", false);
        BigFraction bf = new BigFraction(1, 10);
        verify(qc).setSampleCoeff(bf);
    }
}
