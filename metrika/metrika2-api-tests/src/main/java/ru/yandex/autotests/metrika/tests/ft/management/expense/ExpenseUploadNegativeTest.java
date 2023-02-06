package ru.yandex.autotests.metrika.tests.ft.management.expense;

import com.google.common.collect.ImmutableMap;
import com.google.gson.Gson;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ExpenseParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.EXPENSE)
@Title("Загрузка расходов (негативные)")
public class ExpenseUploadNegativeTest {
    private static final Gson GSON = new Gson();

    private static UserSteps user;
    private static Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void checkUploadWithSettingsWithoutUtmSource() {
        user.onManagementSteps().onExpenseSteps()
                .uploadAndExpectError(counterId,
                        ExpenseTestData.CSV_CONTENT_WITH_CYRILIC, ManagementError.MISSED_MANDATORY_COLUMN,
                        new ExpenseParameters()
                                .withProvider(ExpenseTestData.PROVIDER)
                                .withSettings(GSON.toJson(ExpenseTestData.getDefaultSettings()
                                                .withDefaultColumnValues(ImmutableMap.of())
                                ))

                );
    }

    @Test
    public void checkRemoveWithoutDate() {
        user.onManagementSteps().onExpenseSteps()
                .removeAndExpectError(counterId,
                        ExpenseTestData.CSV_REMOVE_WITHOUT_DATE_CONTENT, ManagementError.MISSED_MANDATORY_COLUMN,
                        new ExpenseParameters()
                                .withProvider(ExpenseTestData.PROVIDER)

                );
    }

    @Test
    public void checkUploadWithSettingsWithNegativeExpenses() {
        user.onManagementSteps().onExpenseSteps()
                .uploadAndExpectError(counterId,
                        ExpenseTestData.CSV_CONTENT_WITH_CYRILIC_NEGATIVE_EXPENSES, ManagementError.INCORRECT_VALUE_IN_COLUMN,
                        new ExpenseParameters()
                                .withProvider(ExpenseTestData.PROVIDER)
                                .withSettings(GSON.toJson(ExpenseTestData.getDefaultSettings()))
                );
    }


    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
