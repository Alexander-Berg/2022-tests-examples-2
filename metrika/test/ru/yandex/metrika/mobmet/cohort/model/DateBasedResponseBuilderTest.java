package ru.yandex.metrika.mobmet.cohort.model;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.List;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.hamcrest.MatcherAssert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.cohort.misc.CABuildContext;
import ru.yandex.metrika.mobmet.cohort.misc.CohortDates;
import ru.yandex.metrika.mobmet.cohort.model.cell.CACell;
import ru.yandex.metrika.mobmet.cohort.model.cell.CADateBasedCell;
import ru.yandex.metrika.mobmet.cohort.response.model.CACohort;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;

import static java.time.LocalTime.MIDNIGHT;
import static org.hamcrest.Matchers.containsString;

/**
 * Created by graev on 27/03/2017.
 */
public class DateBasedResponseBuilderTest {
    private static final CAMetricV1 metric = CAMetricV1.devices;
    private static final String cohortDimension = "";

    private static final long totals_1 = 564;
    private static final long totals_2 = 563;
    private static final long totals_3 = 521;

    private static final double matrix_1_0 = 564;
    private static final double matrix_1_1 = 137;
    private static final double matrix_1_2 = 81;
    private static final double matrix_2_0 = 563;
    private static final double matrix_2_1 = 110;
    private static final double matrix_2_2 = 110;
    private static final double matrix_3_0 = 521;
    private static final double matrix_3_1 = 99;
    private static final double matrix_3_2 = 43;

    private static final List<CHTotalsRow> totalRows = ImmutableList.<CHTotalsRow>builder()
            .add(new CHTotalsRow("2017-03-01", LocalDate.of(2017, 3, 1), totals_1))
            .add(new CHTotalsRow("2017-03-02", LocalDate.of(2017, 3, 2), totals_2))
            .add(new CHTotalsRow("2017-03-03", LocalDate.of(2017, 3, 3), totals_3))
            .build();

    private static final List<CHMatrixRow> matrixRows = ImmutableList.<CHMatrixRow>builder()
            .add(new CHMatrixRow("2017-03-01", LocalDate.of(2017, 3, 1), 0, matrix_1_0))
            .add(new CHMatrixRow("2017-03-01", LocalDate.of(2017, 3, 1), 1, matrix_1_1))
            .add(new CHMatrixRow("2017-03-01", LocalDate.of(2017, 3, 1), 2, matrix_1_2))
            .add(new CHMatrixRow("2017-03-02", LocalDate.of(2017, 3, 2), 0, matrix_2_0))
            .add(new CHMatrixRow("2017-03-02", LocalDate.of(2017, 3, 2), 1, matrix_2_1))
            .add(new CHMatrixRow("2017-03-02", LocalDate.of(2017, 3, 2), 2, matrix_2_2))
            .add(new CHMatrixRow("2017-03-03", LocalDate.of(2017, 3, 3), 0, matrix_3_0))
            .add(new CHMatrixRow("2017-03-03", LocalDate.of(2017, 3, 3), 1, matrix_3_1))
            .add(new CHMatrixRow("2017-03-03", LocalDate.of(2017, 3, 3), 2, matrix_3_2))
            .build();

    private static final CAQueryResult data = new CAQueryResult(matrixRows, totalRows);

    private static final CABuildContext context = new CABuildContext(true, 1L, metric, cohortDimension, true, null, null);

    private static final DateBasedResponseBuilder builder = new DateBasedResponseBuilder();

    @Test
    public void testCompletelyClosedTable() throws JsonProcessingException {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 4, 1), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        // Общий totals это всегда сумма размеров всех
        final long totals = totals_1 + totals_2 + totals_3;

        final CACell day_1_0 = CADateBasedCell.cell(metric, matrix_1_0).withTotals(totals_1);
        final CACell day_1_1 = CADateBasedCell.cell(metric, matrix_1_1).withTotals(totals_1);
        final CACell day_1_2 = CADateBasedCell.cell(metric, matrix_1_2).withTotals(totals_1);

        final CACell day_2_0 = CADateBasedCell.cell(metric, matrix_2_0).withTotals(totals_2);
        final CACell day_2_1 = CADateBasedCell.cell(metric, matrix_2_1).withTotals(totals_2);
        final CACell day_2_2 = CADateBasedCell.cell(metric, matrix_2_2).withTotals(totals_2);

        final CACell day_3_0 = CADateBasedCell.cell(metric, matrix_3_0).withTotals(totals_3);
        final CACell day_3_1 = CADateBasedCell.cell(metric, matrix_3_1).withTotals(totals_3);
        final CACell day_3_2 = CADateBasedCell.cell(metric, matrix_3_2).withTotals(totals_3);

        final CACell bucket_0 = CADateBasedCell.cell(metric, matrix_1_0 + matrix_2_0 + matrix_3_0).withTotals(totals_1 + totals_2 + totals_3);
        final CACell bucket_1 = CADateBasedCell.cell(metric, matrix_1_1 + matrix_2_1 + matrix_3_1).withTotals(totals_1 + totals_2 + totals_3);
        final CACell bucket_2 = CADateBasedCell.cell(metric, matrix_1_2 + matrix_2_2 + matrix_3_2).withTotals(totals_1 + totals_2 + totals_3);

        final CACohort cohort1 = CACohort.dateBased(dates.enclosing("2017-03-01"));
        final CACohort cohort2 = CACohort.dateBased(dates.enclosing("2017-03-02"));
        final CACohort cohort3 = CACohort.dateBased(dates.enclosing("2017-03-03"));

        final CAResponse expectedResponse = new CAResponse(
                totals,
                ImmutableList.of(
                        new CARow(cohort1, ImmutableList.of(day_1_0, day_1_1, day_1_2)),
                        new CARow(cohort2, ImmutableList.of(day_2_0, day_2_1, day_2_2)),
                        new CARow(cohort3, ImmutableList.of(day_3_0, day_3_1, day_3_2))),
                ImmutableList.of(
                        new CACohortTotals(cohort1, totals_1),
                        new CACohortTotals(cohort2, totals_2),
                        new CACohortTotals(cohort3, totals_3)),
                ImmutableList.of(
                        bucket_0,
                        bucket_1,
                        bucket_2
                )
        );

        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        final CAResponse actualResponse = builder.build(context, data, dates);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actualResponse);

        MatcherAssert.assertThat("Rectangular table is the same as expected",
                actualJson, containsString(expectedJson));
    }

    @Test
    public void testMaximallyOpenTable() throws JsonProcessingException {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 3, 3), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        // Общий totals это всегда сумма размеров всех
        final long totals = totals_1 + totals_2 + totals_3;

        final CACell day_1_0 = CADateBasedCell.cell(metric, matrix_1_0).withTotals(totals_1);
        final CACell day_1_1 = CADateBasedCell.cell(metric, matrix_1_1).withTotals(totals_1);
        final CACell day_1_2 = CADateBasedCell.cell(metric, matrix_1_2).withTotals(totals_1);

        final CACell day_2_0 = CADateBasedCell.cell(metric, matrix_2_0).withTotals(totals_2);
        final CACell day_2_1 = CADateBasedCell.cell(metric, matrix_2_1).withTotals(totals_2);

        final CACell day_3_0 = CADateBasedCell.cell(metric, matrix_3_0).withTotals(totals_3);

        final CACell bucket_0 = CADateBasedCell.cell(metric, matrix_1_0 + matrix_2_0).withTotals(totals_1 + totals_2);
        final CACell bucket_1 = CADateBasedCell.cell(metric, matrix_1_1).withTotals(totals_1);
        final CACell bucket_2 = CADateBasedCell.cell(metric, matrix_1_2).withTotals(totals_1);

        final CACohort cohort1 = CACohort.dateBased(dates.enclosing("2017-03-01"));
        final CACohort cohort2 = CACohort.dateBased(dates.enclosing("2017-03-02"));
        final CACohort cohort3 = CACohort.dateBased(dates.enclosing("2017-03-03"));

        final CAResponse expectedResponse = new CAResponse(
                totals,
                ImmutableList.of(
                        new CARow(cohort1, ImmutableList.of(day_1_0, day_1_1, day_1_2)),
                        new CARow(cohort2, ImmutableList.of(day_2_0, day_2_1)),
                        new CARow(cohort3, ImmutableList.of(day_3_0))),
                ImmutableList.of(
                        new CACohortTotals(cohort1, totals_1),
                        new CACohortTotals(cohort2, totals_2),
                        new CACohortTotals(cohort3, totals_3)),
                ImmutableList.of(
                        bucket_0,
                        bucket_1,
                        bucket_2
                )
        );

        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        final CAResponse actualResponse = builder.build(context, data, dates);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actualResponse);

        MatcherAssert.assertThat("Rectangular table is the same as expected",
                actualJson, containsString(expectedJson));

    }

    @Test
    public void testPartiallyOpenTable() throws JsonProcessingException {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03",
                GroupType.day,
                ZonedDateTime.of(LocalDate.of(2017, 3, 4), MIDNIGHT, ZoneId.of("Europe/Moscow")));

        // Общий totals это всегда сумма размеров всех
        final long totals = totals_1 + totals_2 + totals_3;

        final CACell day_1_0 = CADateBasedCell.cell(metric, matrix_1_0).withTotals(totals_1);
        final CACell day_1_1 = CADateBasedCell.cell(metric, matrix_1_1).withTotals(totals_1);
        final CACell day_1_2 = CADateBasedCell.cell(metric, matrix_1_2).withTotals(totals_1);

        final CACell day_2_0 = CADateBasedCell.cell(metric, matrix_2_0).withTotals(totals_2);
        final CACell day_2_1 = CADateBasedCell.cell(metric, matrix_2_1).withTotals(totals_2);
        final CACell day_2_2 = CADateBasedCell.cell(metric, matrix_2_2).withTotals(totals_2);

        final CACell day_3_0 = CADateBasedCell.cell(metric, matrix_3_0).withTotals(totals_3);
        final CACell day_3_1 = CADateBasedCell.cell(metric, matrix_3_1).withTotals(totals_3);

        final CACell bucket_0 = CADateBasedCell.cell(metric, matrix_1_0 + matrix_2_0 + matrix_3_0).withTotals(totals_1 + totals_2 + totals_3);
        final CACell bucket_1 = CADateBasedCell.cell(metric, matrix_1_1 + matrix_2_1).withTotals(totals_1 + totals_2);
        final CACell bucket_2 = CADateBasedCell.cell(metric, matrix_1_2 + matrix_2_2).withTotals(totals_1 + totals_2);

        final CACohort cohort1 = CACohort.dateBased(dates.enclosing("2017-03-01"));
        final CACohort cohort2 = CACohort.dateBased(dates.enclosing("2017-03-02"));
        final CACohort cohort3 = CACohort.dateBased(dates.enclosing("2017-03-03"));

        final CAResponse expectedResponse = new CAResponse(
                totals,
                ImmutableList.of(
                        new CARow(cohort1, ImmutableList.of(day_1_0, day_1_1, day_1_2)),
                        new CARow(cohort2, ImmutableList.of(day_2_0, day_2_1, day_2_2)),
                        new CARow(cohort3, ImmutableList.of(day_3_0, day_3_1))),
                ImmutableList.of(
                        new CACohortTotals(cohort1, totals_1),
                        new CACohortTotals(cohort2, totals_2),
                        new CACohortTotals(cohort3, totals_3)),
                ImmutableList.of(
                        bucket_0,
                        bucket_1,
                        bucket_2
                )
        );

        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        final CAResponse actualResponse = builder.build(context, data, dates);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actualResponse);

        MatcherAssert.assertThat("Rectangular table is the same as expected",
                actualJson, containsString(expectedJson));
    }
}
