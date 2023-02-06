package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.ecommerce;

import com.google.common.collect.ImmutableList;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.SubTable;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bEcommerceTest;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Dimension.subTable;

/**
 * Created by konkov on 28.09.2015.
 */
public abstract class BaseB2bDimensionsEcommerceTest extends BaseB2bEcommerceTest {

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public String metricName;
    

    private static final String METRIC_EACTION = "ym:s:productPurchasedPrice";
    private static final String METRIC_EPURCHASE = "ym:s:ecommercePurchases";

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(CombinatorialBuilder.builder()
                        .values(userOnTest.onMetadataSteps().getDimensionsRaw(
                                dimension(table(TableEnum.VISITS).and(ecommerce())).and(subTable(SubTable.EACTION))))
                        .value(METRIC_EACTION)
                        .build())
                .addAll(CombinatorialBuilder.builder()
                        .values(userOnTest.onMetadataSteps().getDimensionsRaw(
                                dimension(table(TableEnum.VISITS).and(ecommerce())).and(subTable(SubTable.EPURCHASE))))
                        .value(METRIC_EPURCHASE)
                        .build())
                .build();
    }

    @IgnoreParameters.Tag(name = "METR-27539")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:productBrandCart"), anything()},
                {equalTo("ym:s:productNameCart"), anything()},
                {equalTo("ym:s:productIDCart"), anything()}
        });
    }
}
