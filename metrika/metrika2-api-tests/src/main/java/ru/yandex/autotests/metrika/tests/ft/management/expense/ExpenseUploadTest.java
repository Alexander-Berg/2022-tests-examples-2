package ru.yandex.autotests.metrika.tests.ft.management.expense;

import com.google.gson.Gson;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ExpenseParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingStatus;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.EXPENSE)
@Title("Загрузка расходов")
public class ExpenseUploadTest {

    private static final Gson GSON = new Gson();
    public static final BeanDifferMatcher<ExpenseUploading> EXPENSE_UPLOADING_BEAN_DIFFER_MATCHER = beanEquivalent(new ExpenseUploading()
            .withSourceQuantity(1L)
            .withStatus(ExpenseUploadingStatus.UPLOADED)
            .withType(ExpenseUploadingType.EXPENSES)
            .withProvider(ExpenseTestData.PROVIDER)
    ).withVariation(new DefaultMatchVariation()
            .forFields("id", "createTime")
            .useMatcher(notNullValue())
    );

    public static final BeanDifferMatcher<ExpenseUploading> EXPENSE_REMOVE_BEAN_DIFFER_MATCHER = beanEquivalent(new ExpenseUploading()
            .withSourceQuantity(1L)
            .withStatus(ExpenseUploadingStatus.UPLOADED)
            .withType(ExpenseUploadingType.REMOVES)
            .withProvider(ExpenseTestData.PROVIDER)
    ).withVariation(new DefaultMatchVariation()
            .forFields("id", "createTime")
            .useMatcher(notNullValue())
    );

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
    public void checkUpload() {
        ExpenseUploading uploading = user.onManagementSteps().onExpenseSteps()
                .upload(counterId, ExpenseTestData.CSV_CONTENT, new ExpenseParameters().withProvider(ExpenseTestData.PROVIDER));

        assertThat(
                "загрузка корректно создалась",
                uploading,
                EXPENSE_UPLOADING_BEAN_DIFFER_MATCHER
        );
    }

    @Test
    public void checkRemove() {
        ExpenseUploading remove_uploading = user.onManagementSteps().onExpenseSteps()
                .remove(counterId, ExpenseTestData.CSV_REMOVE_CONTENT, new ExpenseParameters()
                        .withProvider(ExpenseTestData.PROVIDER)
                );

        assertThat(
                "загрузка удаления корректно создалась",
                remove_uploading,
                EXPENSE_REMOVE_BEAN_DIFFER_MATCHER
        );
    }

    @Test
    public void checkUploadWithSettings() {
        ExpenseUploading uploading = user.onManagementSteps().onExpenseSteps()
                .upload(counterId, ExpenseTestData.CSV_CONTENT_WITH_CYRILIC, new ExpenseParameters()
                        .withProvider(ExpenseTestData.PROVIDER)
                        .withSettings(GSON.toJson(ExpenseTestData.getDefaultSettings()))
                );

        assertThat(
                "загрузка корректно создалась",
                uploading,
                EXPENSE_UPLOADING_BEAN_DIFFER_MATCHER
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
