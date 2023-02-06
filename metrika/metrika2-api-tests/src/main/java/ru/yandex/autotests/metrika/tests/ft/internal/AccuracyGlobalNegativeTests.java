package ru.yandex.autotests.metrika.tests.ft.internal;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.internal.GetAccuracyParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static ru.yandex.autotests.metrika.errors.InternalError.*;

/**
 * Created by omatikaya on 24.03.17.
 */
@Features(Requirements.Feature.INTERNAL)
@Title("Негативные тесты на ручку get_accuracy/global для сводки")
@RunWith(Parameterized.class)
public class AccuracyGlobalNegativeTests {
    private UserSteps user = new UserSteps();

    @Parameterized.Parameter()
    public String startDate;

    @Parameterized.Parameter(1)
    public String endDate;

    @Parameterized.Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "date1 = {0}, date2 = {1}")
    public static Collection<Object[]> createParameters(){
        return Arrays.asList(new Object[][]{
                {"2016-09-01", "2016-08-08", DATE1_MORE_THAN_DATE2},
                {"2016-09-1", "xxxx-yy-zz", INVALID_DATE2_FORMAT},
                {null, "2016-9-10", INVALID_DATE1_FORMAT}
        });
    }

    @Test
    public void getAccuracyDatesNegative() {
        user.onInternalSteps().getAccuracyGlobalAndExpectError(error,
                new GetAccuracyParameters()
                        .withDate1(startDate)
                        .withDate2(endDate));
    }
}
