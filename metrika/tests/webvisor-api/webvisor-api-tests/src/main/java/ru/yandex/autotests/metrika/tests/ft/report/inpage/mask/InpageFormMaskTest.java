package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.FORM, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Аналитика форм. Маски url")
public class InpageFormMaskTest {
    private static UserSteps user = new UserSteps();

    private MapsV1DataFormGETPOSTSchema resultShipping;
    private MapsV1DataFormGETPOSTSchema resultPayment;
    private MapsV1DataFormGETPOSTSchema resultCart;
    private MapsV1DataFormGETPOSTSchema resultShippingAndPayment;
    private List<List<Long>> cartFunnels;
    private List<List<Long>> paymentFunnels;
    private List<List<Long>> shippingFunnels;
    private List<List<Long>> shippingAndPaymentFunnels;
    private List<List<Long>> shippingPlusPaymentFunnels;

    @Before
    public void setup() {
        resultShipping = getResultForUrl(InpageTestData.getShippingUrl());
        resultPayment = getResultForUrl(InpageTestData.getPaymentUrl());
        resultCart = getResultForUrl(InpageTestData.getCartUrl());
        resultShippingAndPayment = getResultForUrl(InpageTestData.getShippingOrPaymentUrl());

        assumeThat("Данные для cart есть", resultCart.getForms(), not(empty()));
        assumeThat("Данные для shipping есть", resultShipping.getForms(), not(empty()));
        assumeThat("Данные для payment есть", resultPayment.getForms(), not(empty()));
        assumeThat("Данные для shippingAndPayment есть", resultShippingAndPayment.getForms(), not(empty()));

        paymentFunnels = user.onResultSteps().getFormsFunnels(resultPayment);
        shippingFunnels = user.onResultSteps().getFormsFunnels(resultShipping);
        int formsToCheck = Math.min(shippingFunnels.size(), paymentFunnels.size());
        paymentFunnels = paymentFunnels.subList(0, formsToCheck);
        shippingFunnels = shippingFunnels.subList(0, formsToCheck);
        cartFunnels = user.onResultSteps().getFormsFunnels(resultCart).subList(0, formsToCheck);
        shippingAndPaymentFunnels = user.onResultSteps().getFormsFunnels(resultShippingAndPayment).subList(0, formsToCheck);

        shippingPlusPaymentFunnels = user.onResultSteps().funnelsPlus(shippingFunnels, paymentFunnels);
    }

    @Test
    public void cartIsGreaterEqualThanShippingPlusPayment() {
        assertThat("funnel форм для cart минус shipping + payment не меньше 0",
                user.onResultSteps().funnelsMinus(cartFunnels, shippingPlusPaymentFunnels),
                everyItem(everyItem(greaterThanOrEqualTo(0L))));
    }

    @Test
    public void shippingAndPaymentIsEqualShippingPlusPayment() {
        assertThat("funnel форм для shipping|payment минус shipping + payment равно 0",
                user.onResultSteps().funnelsMinus(shippingAndPaymentFunnels, shippingPlusPaymentFunnels),
                everyItem(everyItem(equalTo(0L))));
    }

    private MapsV1DataFormGETPOSTSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageFormDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
