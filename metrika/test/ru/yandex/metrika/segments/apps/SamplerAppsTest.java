package ru.yandex.metrika.segments.apps;

import java.util.Collection;
import java.util.Optional;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.apache.commons.math3.fraction.BigFraction;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.apps.schema.MobmetTableSchema;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.parts.FromBaseTable;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.segments.apps.schema.MtMobLog.generic_events_all;
import static ru.yandex.metrika.segments.apps.schema.MtMobLog.generic_events_layer;

@RunWith(Parameterized.class)
public class SamplerAppsTest {

    private static final double DELTA = 0.0000001;

    @Parameterized.Parameter
    public long predictedRowsCount;

    @Parameterized.Parameter(1)
    public String accuracy;

    @Parameterized.Parameter(2)
    public boolean proposedAccuracy;

    @Parameterized.Parameter(3)
    public QueryContext expectedContext;

    @Test
    public void test() {
        QueryContext queryContext = buildContextStub();
        Query query = buildQueryMock(queryContext);
        SamplerApps sampler = buildSamplerStub(predictedRowsCount);
        sampler.setSampleSize(query, accuracy, proposedAccuracy);

        assertEquals(expectedContext.getSampleSpace(), queryContext.getSampleSpace());
        assertEquals(expectedContext.isSampleable(), queryContext.isSampleable());
        assertEquals(expectedContext.getMaxSampleShare(), queryContext.getMaxSampleShare(), DELTA);
        assertEquals(expectedContext.getSampleCoeff(), queryContext.getSampleCoeff());
        assertEquals(expectedContext.getSampleSize(), queryContext.getSampleSize(), DELTA);
    }

    @Parameterized.Parameters(name = "predicted row count {0}, accuracy {1}, proposedAccuracy {2}, expectedContext {3}")
    public static Collection<Object[]> initParams() {
        return new ImmutableList.Builder<Object[]>()
                .add(params(10, "0.25", false,
                        qc().sampleSpace(10).sampleable(false).maxSampleShare(1.0)
                                .sampleCoeff(new BigFraction(1, 4)).sampleSize(3).build()))
                .add(params(9_999_976, "0.25", true,
                        qc().sampleSpace(9_999_976).sampleable(false).maxSampleShare(1.0)
                                .sampleCoeff(BigFraction.ONE).sampleSize(9_999_976).build()))
                .add(params(10, "medium", true,
                        qc().sampleSpace(10).sampleable(false).maxSampleShare(1.0)
                                .sampleCoeff(BigFraction.ONE).sampleSize(10).build()))
                .add(params(999, "low", true,
                        qc().sampleSpace(999).sampleable(false).maxSampleShare(1.0)
                                .sampleCoeff(BigFraction.ONE).sampleSize(999).build()))
                .add(params(99_000_000, "high", true,
                        qc().sampleSpace(99_000_000).sampleable(true).maxSampleShare(0.1)
                                .sampleCoeff(BigFraction.ONE).sampleSize(99_000_000).build()))
                .add(params(99_000_000, "full", true,
                        qc().sampleSpace(99_000_000).sampleable(true).maxSampleShare(0.1)
                                .sampleCoeff(BigFraction.ONE).sampleSize(99_000_000).build()))
                .add(params(1_000_000_000, "10", true,
                        qc().sampleSpace(1_000_000_000).sampleable(true).maxSampleShare(0.01)
                                .sampleCoeff(BigFraction.ONE).sampleSize(1_000_000_000).build()))
                .add(params(1_000_000_000, "iavkd", true,
                        qc().sampleSpace(1_000_000_000).sampleable(true).maxSampleShare(0.01)
                                .sampleCoeff(BigFraction.ONE).sampleSize(1_000_000_000).build()))
                .build();
    }

    private static Object[] params(Object... params) {
        return params;
    }

    private static QueryContext.Builder qc() {
        return QueryContext.newBuilder()
                .targetTable(MobmetTableSchema.GENERIC_EVENTS)
                .enableSampling(true)
                .idsByName(ImmutableMap.of(MobmetTableSchema.APP_ID, new int[1]))
                .startDate("2017-01-01")
                .endDate("2017-01-01");
    }

    private static QueryContext buildContextStub() {
        return qc().build();
    }

    private static Query buildQueryMock(QueryContext queryContext) {
        Query query = mock(Query.class);
        when(query.getQueryContext()).thenReturn(queryContext);
        when(query.getDimensionFilters()).thenReturn(Optional.empty());
        when(query.getMetricFilters()).thenReturn(Optional.empty());
        when(query.getFromTable()).thenReturn(new FromBaseTable(generic_events_layer, generic_events_all));
        return query;
    }

    private static SamplerApps buildSamplerStub(long rowCount) {
        return new SamplerApps((a, b, c) -> rowCount, new MobmetTableSchema());
    }
}
