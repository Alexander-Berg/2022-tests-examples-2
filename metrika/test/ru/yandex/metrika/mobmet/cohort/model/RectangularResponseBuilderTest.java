package ru.yandex.metrika.mobmet.cohort.model;

import java.io.IOException;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.Collections;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.mobmet.cohort.misc.CABuildContext;
import ru.yandex.metrika.mobmet.cohort.misc.CohortDates;
import ru.yandex.metrika.mobmet.cohort.model.cell.CACell;
import ru.yandex.metrika.mobmet.cohort.model.cell.CAGroupedDatesCell;
import ru.yandex.metrika.mobmet.cohort.response.model.CACohort;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;

import static java.time.LocalTime.MIDNIGHT;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;

/**
 * Тестируем построение прямоугольной таблицы по ответу КХ
 * <p>
 * Created by graev on 26/03/2017.
 */
@RunWith(Parameterized.class)
public class RectangularResponseBuilderTest {

    private static final String cohortDimension = "";
    private static final LocalDate cohortFetcherDate1 = null;
    private static final LocalDate cohortFetcherDate2 = null;
    private static final CAMetricV1 metric = CAMetricV1.devices;

    private static final long totals_organic_1 = 564;
    private static final long totals_organic_2 = 563;
    private static final long totals_organic_3 = 521;
    private static final long totals_portal_1 = 56;
    private static final long totals_portal_2 = 52;
    private static final long totals_portal_3 = 51;

    private static final double matrix_organic_1_0 = 564;
    private static final double matrix_organic_1_1 = 137;
    private static final double matrix_organic_1_2 = 81;
    private static final double matrix_organic_2_0 = 563;
    private static final double matrix_organic_2_1 = 110;
    private static final double matrix_organic_2_2 = 110;
    private static final double matrix_organic_3_0 = 521;
    private static final double matrix_organic_3_1 = 99;
    private static final double matrix_organic_3_2 = 43;
    private static final double matrix_portal_1_0 = 56;
    private static final double matrix_portal_1_1 = 7;
    private static final double matrix_portal_1_2 = 1;
    private static final double matrix_portal_2_0 = 52;
    private static final double matrix_portal_2_1 = 14;
    private static final double matrix_portal_2_2 = 7;
    private static final double matrix_portal_3_0 = 51;
    private static final double matrix_portal_3_1 = 21;
    private static final double matrix_portal_3_2 = 2;

    private static final List<CHTotalsRow> totalRows = ImmutableList.<CHTotalsRow>builder()
            .add(new CHTotalsRow("0", LocalDate.of(2017, 3, 1), totals_organic_1))
            .add(new CHTotalsRow("0", LocalDate.of(2017, 3, 2), totals_organic_2))
            .add(new CHTotalsRow("0", LocalDate.of(2017, 3, 3), totals_organic_3))
            .add(new CHTotalsRow("254", LocalDate.of(2017, 3, 1), totals_portal_1))
            .add(new CHTotalsRow("254", LocalDate.of(2017, 3, 2), totals_portal_2))
            .add(new CHTotalsRow("254", LocalDate.of(2017, 3, 3), totals_portal_3))
            .build();

    private static final List<CHMatrixRow> matrixRows = ImmutableList.<CHMatrixRow>builder()
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 1), 0, matrix_organic_1_0))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 1), 1, matrix_organic_1_1))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 1), 2, matrix_organic_1_2))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 2), 0, matrix_organic_2_0))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 2), 1, matrix_organic_2_1))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 2), 2, matrix_organic_2_2))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 3), 0, matrix_organic_3_0))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 3), 1, matrix_organic_3_1))
            .add(new CHMatrixRow("0", LocalDate.of(2017, 3, 3), 2, matrix_organic_3_2))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 1), 0, matrix_portal_1_0))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 1), 1, matrix_portal_1_1))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 1), 2, matrix_portal_1_2))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 2), 0, matrix_portal_2_0))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 2), 1, matrix_portal_2_1))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 2), 2, matrix_portal_2_2))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 3), 0, matrix_portal_3_0))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 3), 1, matrix_portal_3_1))
            .add(new CHMatrixRow("254", LocalDate.of(2017, 3, 3), 2, matrix_portal_3_2))
            .build();

    private static final CAQueryResult data = new CAQueryResult(matrixRows, totalRows);

    @Parameter
    public boolean propagateMetricForFuture;

    private int propagateForFuture;

    private CABuildContext context;

    private RectangularResponseBuilder builder;

    @Parameters(name = "propagateForFuture = {0}")
    public static Object[] propagateForFuture() {
        return new Object[]{false, true};
    }

    @Before
    public void setUp() throws Exception {
        propagateForFuture = propagateMetricForFuture ? 1 : 0;
        context = new CABuildContext(
                true, 1L, metric, cohortDimension, propagateMetricForFuture, cohortFetcherDate1, cohortFetcherDate2);
        builder = new RectangularResponseBuilder(
                (context, keys) -> keys.stream()
                        .map(k -> CACohort.partner(k, k, k.equals("0") ? PartnerType.ORGANIC : PartnerType.ORDINARY))
                        .collect(Collectors.toMap(CACohort::getId, Function.identity()))
        );
    }

    /**
     * Тестируем построение таблицы, которая находится далеко в прошлом
     */
    @Test
    public void testCompletelyClosedTable() throws IOException {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 4, 1), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        // Общий totals это всегда сумма размеров всех
        final long totals = totals_organic_1 + totals_organic_2 + totals_organic_3 + totals_portal_1 + totals_portal_2 + totals_portal_3;

        // Размеры когорт можно суммировать по ответу КХ
        final long organic_cohort = totals_organic_1 + totals_organic_2 + totals_organic_3;

        final long portal_cohort = totals_portal_1 + totals_portal_2 + totals_portal_3;

        final CACell day_0_totals = new CAGroupedDatesCell(metric, matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0
                + matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0, organic_cohort + portal_cohort);

        final CACell day_1_totals = new CAGroupedDatesCell(metric, matrix_organic_1_1 + matrix_organic_2_1 + matrix_organic_3_1
                + matrix_portal_1_1 + matrix_portal_2_1 + matrix_portal_3_1, organic_cohort + portal_cohort);

        final CACell day_2_totals = new CAGroupedDatesCell(metric, matrix_organic_1_2 + matrix_organic_2_2 + matrix_organic_3_2
                + matrix_portal_1_2 + matrix_portal_2_2 + matrix_portal_3_2, organic_cohort + portal_cohort);

        final CACell organic_0 = new CAGroupedDatesCell(metric, matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0, organic_cohort);

        final CACell organic_1 = new CAGroupedDatesCell(metric, matrix_organic_1_1 + matrix_organic_2_1 + matrix_organic_3_1, organic_cohort);

        final CACell organic_2 = new CAGroupedDatesCell(metric, matrix_organic_1_2 + matrix_organic_2_2 + matrix_organic_3_2, organic_cohort);

        final CACell portal_0 = new CAGroupedDatesCell(metric, matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0, portal_cohort);

        final CACell portal_1 = new CAGroupedDatesCell(metric, matrix_portal_1_1 + matrix_portal_2_1 + matrix_portal_3_1, portal_cohort);

        final CACell portal_2 = new CAGroupedDatesCell(metric, matrix_portal_1_2 + matrix_portal_2_2 + matrix_portal_3_2, portal_cohort);

        final CACohort organicCohort = CACohort.partner("0", "0", PartnerType.ORGANIC);
        final CACohort portalCohort = CACohort.partner("254", "254", PartnerType.ORDINARY);

        final CAResponse expectedResponse = new CAResponse(
                totals,
                ImmutableList.of(
                        new CARow(organicCohort, ImmutableList.of(organic_0, organic_1, organic_2)),
                        new CARow(portalCohort, ImmutableList.of(portal_0, portal_1, portal_2))),
                ImmutableList.of(
                        new CACohortTotals(organicCohort, organic_cohort),
                        new CACohortTotals(portalCohort, portal_cohort)),
                ImmutableList.of(
                        day_0_totals,
                        day_1_totals,
                        day_2_totals
                )
        );

        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        final CAResponse actualResponse = builder.build(context, data, dates);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actualResponse);

        assertThat("Rectangular table is the same as expected",
                actualJson, containsString(expectedJson));
    }

    /**
     * Тестируем построение таблицы, которая своей правой границей упирается в сегодняшний день
     */
    @Test
    public void testMaximallyOpenTable() throws IOException {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 3, 3), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        // Общий totals это всегда сумма размеров всех
        final long totals = totals_organic_1 + totals_organic_2 + totals_organic_3 + totals_portal_1 + totals_portal_2 + totals_portal_3;

        // Размеры когорт можно суммировать по ответу КХ
        final long organic_cohort = totals_organic_1 + totals_organic_2 + totals_organic_3;

        final long portal_cohort = totals_portal_1 + totals_portal_2 + totals_portal_3;

        final CACell day_0_totals = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_portal_1_0 + matrix_portal_2_0 + (matrix_organic_3_0 + matrix_portal_3_0),
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_portal_1_0 + matrix_portal_2_0 + (matrix_organic_3_0 + matrix_portal_3_0) * propagateForFuture,
                totals_organic_1 + totals_organic_2 + totals_portal_1 + totals_portal_2 + (totals_organic_3 + totals_portal_3) * propagateForFuture);

        final CACell day_1_totals = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_1 + matrix_portal_1_1 + matrix_organic_2_1 + matrix_portal_2_1 + (matrix_organic_3_1 + matrix_portal_3_1) * propagateForFuture,
                matrix_organic_1_1 + matrix_portal_1_1 + (matrix_organic_2_1 + matrix_organic_3_1 + matrix_portal_2_1 + matrix_portal_3_1) * propagateForFuture,
                totals_organic_1 + totals_portal_1 + (totals_organic_2 + totals_organic_3 + totals_portal_2 + totals_portal_3) * propagateForFuture);

        // Это максимальный бакет, поэтому незакрытый период это ОК
        final CACell day_2_totals = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_2 + matrix_portal_1_2 + (matrix_organic_2_2 + matrix_organic_3_2 + matrix_portal_2_2 + matrix_portal_3_2) * propagateForFuture,
                matrix_organic_1_2 + matrix_portal_1_2 + (matrix_organic_2_2 + matrix_organic_3_2 + matrix_portal_2_2 + matrix_portal_3_2) * propagateForFuture,
                totals_organic_1 + totals_portal_1 + (totals_organic_2 + totals_organic_3 + totals_portal_2 + totals_portal_3) * propagateForFuture);

        final CACell organic_0 = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0 * propagateForFuture,
                totals_organic_1 + totals_organic_2 + totals_organic_3 * propagateForFuture);

        final CACell organic_1 = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_1 + matrix_organic_2_1 + matrix_organic_3_1 * propagateForFuture,
                matrix_organic_1_1 + (matrix_organic_2_1 + matrix_organic_3_1) * propagateForFuture,
                totals_organic_1 + (totals_organic_2 + totals_organic_3) * propagateForFuture);

        final CACell organic_2 = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_2 + (matrix_organic_2_2 + matrix_organic_3_2) * propagateForFuture,
                matrix_organic_1_2 + (matrix_organic_2_2 + matrix_organic_3_2) * propagateForFuture,
                totals_organic_1 + (totals_organic_2 + totals_organic_3) * propagateForFuture);

        final CACell portal_0 = new CAGroupedDatesCell(
                metric,
                matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0,
                matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0 * propagateForFuture,
                totals_portal_1 + totals_portal_2 + totals_portal_3 * propagateForFuture);

        final CACell portal_1 = new CAGroupedDatesCell(
                metric,
                matrix_portal_1_1 + matrix_portal_2_1 + matrix_portal_3_1 * propagateForFuture,
                matrix_portal_1_1 + (matrix_portal_2_1 + matrix_portal_3_1) * propagateForFuture,
                totals_portal_1 + (totals_portal_2 + totals_portal_3) * propagateForFuture);

        final CACell portal_2 = new CAGroupedDatesCell(
                metric,
                matrix_portal_1_2 + (matrix_portal_2_2 + matrix_portal_3_2) * propagateForFuture,
                matrix_portal_1_2 + (matrix_portal_2_2 + matrix_portal_3_2) * propagateForFuture,
                totals_portal_1 + (totals_portal_2 + totals_portal_3) * propagateForFuture);

        final CACohort organicCohort = CACohort.partner("0", "0", PartnerType.ORGANIC);
        final CACohort portalCohort = CACohort.partner("254", "254", PartnerType.ORDINARY);

        final CAResponse expectedResponse = new CAResponse(
                totals,
                ImmutableList.of(
                        new CARow(organicCohort, ImmutableList.of(organic_0, organic_1, organic_2)),
                        new CARow(portalCohort, ImmutableList.of(portal_0, portal_1, portal_2))),
                ImmutableList.of(
                        new CACohortTotals(organicCohort, organic_cohort),
                        new CACohortTotals(portalCohort, portal_cohort)),
                ImmutableList.of(
                        day_0_totals,
                        day_1_totals,
                        day_2_totals
                )
        );

        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        final CAResponse actualResponse = builder.build(context, data, dates);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actualResponse);

        assertThat("Rectangular table is the same as expected",
                actualJson, containsString(expectedJson));
    }

    /**
     * Тестируем построение таблицы, у которой часть событий будет находиться в открытом периоде
     */
    @Test
    public void testPartiallyOpenTable() throws IOException {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 3, 4), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        // Общий totals это всегда сумма размеров всех
        final long totals = totals_organic_1 + totals_organic_2 + totals_organic_3 + totals_portal_1 + totals_portal_2 + totals_portal_3;

        // Размеры когорт можно суммировать по ответу КХ
        final long organic_cohort = totals_organic_1 + totals_organic_2 + totals_organic_3;

        final long portal_cohort = totals_portal_1 + totals_portal_2 + totals_portal_3;

        final CACell day_0_totals = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0 + matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0 + matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0,
                totals_organic_1 + totals_organic_2 + totals_organic_3 + totals_portal_1 + totals_portal_2 + totals_portal_3);

        final CACell day_1_totals = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_1 + matrix_organic_2_1 + matrix_portal_1_1 + matrix_portal_2_1 + (matrix_organic_3_1 + matrix_portal_3_1),
                matrix_organic_1_1 + matrix_organic_2_1 + matrix_portal_1_1 + matrix_portal_2_1 + (matrix_organic_3_1 + matrix_portal_3_1) * propagateForFuture,
                totals_organic_1 + totals_organic_2 + totals_portal_1 + totals_portal_2 + (totals_organic_3 + totals_portal_3) * propagateForFuture);

        // Это максимальный бакет, поэтому незакрытый период это ОК
        final CACell day_2_totals = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_2 + matrix_organic_2_2 + matrix_portal_1_2 + matrix_portal_2_2 + (matrix_organic_3_2 + matrix_portal_3_2) * propagateForFuture,
                matrix_organic_1_2 + matrix_organic_2_2 + matrix_portal_1_2 + matrix_portal_2_2 + (matrix_organic_3_2 + matrix_portal_3_2) * propagateForFuture,
                totals_organic_1 + totals_organic_2 + totals_portal_1 + totals_portal_2 + (totals_organic_3 + totals_portal_3) * propagateForFuture);

        final CACell organic_0 = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0,
                matrix_organic_1_0 + matrix_organic_2_0 + matrix_organic_3_0,
                totals_organic_1 + totals_organic_2 + totals_organic_3);

        final CACell organic_1 = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_1 + matrix_organic_2_1 + matrix_organic_3_1,
                matrix_organic_1_1 + matrix_organic_2_1 + matrix_organic_3_1 * propagateForFuture,
                totals_organic_1 + totals_organic_2 + totals_organic_3 * propagateForFuture);

        final CACell organic_2 = new CAGroupedDatesCell(
                metric,
                matrix_organic_1_2 + matrix_organic_2_2 + matrix_organic_3_2 * propagateForFuture,
                matrix_organic_1_2 + matrix_organic_2_2 + matrix_organic_3_2 * propagateForFuture,
                totals_organic_1 + totals_organic_2 + totals_organic_3 * propagateForFuture);

        final CACell portal_0 = new CAGroupedDatesCell(
                metric,
                matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0,
                matrix_portal_1_0 + matrix_portal_2_0 + matrix_portal_3_0,
                totals_portal_1 + totals_portal_2 + totals_portal_3);

        final CACell portal_1 = new CAGroupedDatesCell(
                metric,
                matrix_portal_1_1 + matrix_portal_2_1 + matrix_portal_3_1,
                matrix_portal_1_1 + matrix_portal_2_1 + matrix_portal_3_1 * propagateForFuture,
                totals_portal_1 + totals_portal_2 + totals_portal_3 * propagateForFuture);

        final CACell portal_2 = new CAGroupedDatesCell(
                metric,
                matrix_portal_1_2 + matrix_portal_2_2 + matrix_portal_3_2 * propagateForFuture,
                matrix_portal_1_2 + matrix_portal_2_2 + matrix_portal_3_2 * propagateForFuture,
                totals_portal_1 + totals_portal_2 + totals_portal_3 * propagateForFuture);

        final CACohort organicCohort = CACohort.partner("0", "0", PartnerType.ORGANIC);
        final CACohort portalCohort = CACohort.partner("254", "254", PartnerType.ORDINARY);

        final CAResponse expectedResponse = new CAResponse(
                totals,
                ImmutableList.of(
                        new CARow(organicCohort, ImmutableList.of(organic_0, organic_1, organic_2)),
                        new CARow(portalCohort, ImmutableList.of(portal_0, portal_1, portal_2))),
                ImmutableList.of(
                        new CACohortTotals(organicCohort, organic_cohort),
                        new CACohortTotals(portalCohort, portal_cohort)),
                ImmutableList.of(
                        day_0_totals,
                        day_1_totals,
                        day_2_totals
                )
        );

        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        final CAResponse actualResponse = builder.build(context, data, dates);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actualResponse);

        assertThat("Rectangular table is the same as expected",
                actualJson, containsString(expectedJson));
    }

    @Test
    public void testMinCohortSizeCutsSomething() {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 4, 1), MIDNIGHT, ZoneId.of("Europe/Moscow")));


        // Bigger than portal, less than organic
        final long minCohortSize = (totals_portal_1 + totals_portal_2 + totals_portal_3 +
                totals_organic_1 + totals_organic_2 + totals_organic_3) / 2;
        final CAResponse result = builder.build(
                new CABuildContext(false,
                        minCohortSize, metric, cohortDimension, propagateMetricForFuture, cohortFetcherDate1, cohortFetcherDate2),
                data,
                dates);

        assertThat("Totals and table have equal height", result.getCohortTotals().size(), equalTo(result.getTable().size()));
        assertThat("MinCohortSize cuts Portal tracker from result", result.getCohortTotals().size(), equalTo(1));
    }

    @Test
    public void testMinCohortSizeCutsNone() {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 4, 1), MIDNIGHT, ZoneId.of("Europe/Moscow")));


        // Bigger than portal and organic
        final long minCohortSize = Math.min(totals_portal_1 + totals_portal_2 + totals_portal_3,
                totals_organic_1 + totals_organic_2 + totals_organic_3);
        final CAResponse result = builder.build(
                new CABuildContext(false,
                        minCohortSize, metric, cohortDimension, propagateMetricForFuture, cohortFetcherDate1, cohortFetcherDate2),
                data,
                dates);

        assertThat("Totals and table have equal height", result.getCohortTotals().size(), equalTo(result.getTable().size()));
        assertThat("MinCohortSize does not cut any rows", result.getCohortTotals().size(), equalTo(2));
    }

    @Test
    public void testMinCohortSizeCutsAll() {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 4, 1), MIDNIGHT, ZoneId.of("Europe/Moscow")));


        // Bigger than portal and organic
        final long minCohortSize = Math.max(totals_portal_1 + totals_portal_2 + totals_portal_3,
                totals_organic_1 + totals_organic_2 + totals_organic_3) + 1;
        final CAResponse result = builder.build(
                new CABuildContext(false,
                        minCohortSize, metric, cohortDimension, propagateMetricForFuture, cohortFetcherDate1, cohortFetcherDate2),
                data,
                dates);

        assertThat("Totals and table have equal height", result.getCohortTotals().size(), equalTo(result.getTable().size()));
        assertThat("MinCohortSize does not cut any rows", result.getCohortTotals().size(), equalTo(0));
    }

    /**
     * В тестовом приложении не выполняются инварианты.
     * Чтобы не ждать пока ядро это исправит, сделаем костыль, который просто не будет падать.
     * <p>
     * MOBMET-6539
     */
    @Test
    public void testInconsistentDemoApplicationDoesNotFail() {
        final CohortDates dates = new CohortDates("2017-08-01", "2017-08-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 9, 1), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        final CAQueryResult inconsistentDemoData = new CAQueryResult(Collections.emptyList(), totalRows);
        final CABuildContext demoContext = context
                .inDemoApplication()
                .doNotPopulateZeroRows();

        builder.build(demoContext, inconsistentDemoData, dates); // It just should not fail
    }

}
