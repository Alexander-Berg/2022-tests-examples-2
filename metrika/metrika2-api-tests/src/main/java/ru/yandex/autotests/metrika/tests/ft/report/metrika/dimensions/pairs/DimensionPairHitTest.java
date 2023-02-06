package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions.pairs;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nonParameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.utils.Utils.makePairs;
import static ru.yandex.autotests.metrika.utils.Utils.makeStringPairs;

/**
 * Created by konkov on 25.08.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Пары измерений по просмотрам")
@RunWith(Parameterized.class)
public class DimensionPairHitTest extends DimensionPairsBaseTest {

    @Parameterized.Parameters(name = "Измерения {0}")
    public static Collection createParameters() {
        return makePairs(
                makeStringPairs(
                        HIT_DIMENSIONS,
                        user.onMetadataSteps().getDimensions(table(TableEnum.HITS))),
                user.onMetadataSteps().getMetrics(table(TableEnum.HITS).and(nonParameterized()))
                        .stream().findFirst().get());
    }
}
