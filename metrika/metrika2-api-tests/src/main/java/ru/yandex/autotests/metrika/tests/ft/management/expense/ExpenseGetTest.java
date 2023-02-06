package ru.yandex.autotests.metrika.tests.ft.management.expense;

import java.util.List;

import org.hamcrest.Matchers;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ExpenseParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.expense.ExpenseTestData.COMMENT;
import static ru.yandex.autotests.metrika.tests.ft.management.expense.ExpenseTestData.CSV_CONTENT_SIZE;
import static ru.yandex.autotests.metrika.tests.ft.management.expense.ExpenseTestData.PROVIDER;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.EXPENSE)
@Title("Загрузка расходов")
public class ExpenseGetTest {

    private static UserSteps user;
    private static Long counterId;
    private static ExpenseUploading uploading;
    private static ExpenseUploading removeUploading;
    private static String content;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
        content = ExpenseTestData.CSV_CONTENT;
        uploading = user.onManagementSteps().onExpenseSteps()
                .upload(counterId, content, new ExpenseParameters()
                        .withProvider(PROVIDER)
                        .withComment(COMMENT));
        removeUploading = user.onManagementSteps().onExpenseSteps()
                .remove(counterId, ExpenseTestData.CSV_REMOVE_CONTENT, new ExpenseParameters()
                        .withProvider(ExpenseTestData.PROVIDER)
                );
    }

    @Test
    public void checkGetSingle() {
        ExpenseUploading newUploading = user.onManagementSteps().onExpenseSteps()
                .getUploading(counterId, uploading.getId());

        assertThat("вернулась корректная загрузка", newUploading, beanEquivalent(new ExpenseUploading()
                .withId(uploading.getId())
                .withSourceQuantity((long) CSV_CONTENT_SIZE)
                .withType(ExpenseUploadingType.EXPENSES)
                .withComment(COMMENT)
        ).withVariation(new DefaultMatchVariation()
                .forFields("createTime")
                .useMatcher(notNullValue())
        ));
    }

    @Test
    public void checkGetSingleRemove() {
        ExpenseUploading newUploading = user.onManagementSteps().onExpenseSteps()
                .getUploading(counterId, removeUploading.getId());

        assertThat("вернулась корректная загрузка удалений", newUploading, beanEquivalent(new ExpenseUploading()
                .withId(removeUploading.getId())
                .withSourceQuantity((long) CSV_CONTENT_SIZE)
                .withType(ExpenseUploadingType.REMOVES)
        ).withVariation(new DefaultMatchVariation()
                .forFields("createTime")
                .useMatcher(notNullValue())
        ));
    }

    @Test
    public void checkGetList() {
        List<ExpenseUploading> uploadingsForCounter = user.onManagementSteps().onExpenseSteps()
                .getUploadings(counterId);

        assertThat("вернулся корректный список загрузок", uploadingsForCounter, Matchers.<Iterable<ExpenseUploading>>allOf(
                iterableWithSize(greaterThanOrEqualTo(1)),
                hasItem(
                        beanEquivalent(new ExpenseUploading()
                                .withId(uploading.getId())
                                .withSourceQuantity((long) CSV_CONTENT_SIZE)
                                .withProvider(PROVIDER)
                                .withComment(COMMENT)
                        ).withVariation(new DefaultMatchVariation()
                                .forFields("createTime", "type")
                                .useMatcher(notNullValue())
                        )
                )
        ));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
