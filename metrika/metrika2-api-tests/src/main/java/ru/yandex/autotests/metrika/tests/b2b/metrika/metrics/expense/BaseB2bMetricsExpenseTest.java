package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.expense;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bExpenseTest;

public abstract class BaseB2bMetricsExpenseTest extends BaseB2bExpenseTest {

    public static final List<String> METRICS = Arrays.asList(
            String.join(",",
                    "ym:ev:expenses<currency>",
                    "ym:ev:expenseClicks",
                    "ym:ev:visits",
                    "ym:ev:users"
            ),
            String.join(",",
                    "ym:ev:ecommerce<currency>ConvertedRevenue",
                    "ym:ev:ecommerce<currency>ConvertedRevenuePerVisit",
                    "ym:ev:ecommerce<currency>ConvertedRevenuePerPurchase",
                    "ym:ev:expense<currency>CPC",
                    "ym:ev:expense<currency>EcommerceROI",
                    "ym:ev:expense<currency>EcommerceCRR",
                    "ym:ev:expense<currency>EcommerceCPA"
            ),
            String.join(",",
                    "ym:ev:goal<goal_id>visits",
                    "ym:ev:goal<goal_id>users",
                    "ym:ev:goal<goal_id>converted<currency>Revenue",
                    "ym:ev:goal<goal_id>expense<currency>ROI",
                    "ym:ev:goal<goal_id>expense<currency>CRR",
                    "ym:ev:goal<goal_id>expense<currency>ReachCPA",
                    "ym:ev:goal<goal_id>expense<currency>VisitCPA",
                    "ym:ev:goal<goal_id>expense<currency>UserCPA"
            )
    );

    public static final String DIMENSION = "ym:ev:<attribution>ExpenseSource";

    @Parameterized.Parameter
    public String metricName;

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder()
                .values(METRICS)
                .build();
    }
}
