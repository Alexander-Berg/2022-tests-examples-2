package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.expense;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bExpenseTest;

public abstract class BaseB2bDimensionsExpenseTest extends BaseB2bExpenseTest {

    public static final List<String> DIMENSIONS = Arrays.asList(
            String.join(",",
                    "ym:ev:<attribution>ExpenseSource",
                    "ym:ev:<attribution>ExpenseMedium",
                    "ym:ev:<attribution>ExpenseCampaign",
                    "ym:ev:<attribution>ExpenseTerm",
                    "ym:ev:<attribution>ExpenseContent"
            ),
            String.join(",",
                    "ym:ev:<attribution>UTMSource",
                    "ym:ev:<attribution>UTMMedium",
                    "ym:ev:<attribution>UTMCampaign",
                    "ym:ev:<attribution>UTMTerm",
                    "ym:ev:<attribution>UTMContent"
            )
    );

    public static final String METRIC = "ym:ev:expenses<currency>";

    @Parameterized.Parameter
    public String dimensionName;

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder()
                .values(DIMENSIONS)
                .build();
    }
}
