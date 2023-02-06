package ru.yandex.autotests.metrika.tests.ft.management.expense;

import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.gson.Gson;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ExpenseParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingColumnSettings;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasEntry;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.expense.ExpenseTestData.DEFAULT_UTM_SOURCE;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.EXPENSE)
@Title("Загрузка расходов, чтение настроек")
public class ExpenseSettingsGetTest {
    private static final Gson GSON = new Gson();

    private static UserSteps user;
    private static Long counterId;
    private static ExpenseUploading expenseUploading;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
        expenseUploading = user.onManagementSteps().onExpenseSteps()
                .upload(counterId, ExpenseTestData.CSV_CONTENT_WITH_CYRILIC, new ExpenseParameters()
                        .withProvider(ExpenseTestData.PROVIDER)
                        .withSettings(GSON.toJson(ExpenseTestData.getDefaultSettings())
                        )
                );

    }

    @Test
    public void checkUploadWithSettings() {
        Map<String, ExpenseUploadingColumnSettings> expensesSettings =
                user.onManagementSteps().onExpenseSteps().getExpensesSettings(counterId);

        assertThat("настройки маппинга колонок совпадают", expensesSettings,
                allOf(
                        ImmutableList.of(hasEntry(equalTo(DEFAULT_UTM_SOURCE), equalTo(ExpenseTestData.getDefaultSettings())))
                )
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
