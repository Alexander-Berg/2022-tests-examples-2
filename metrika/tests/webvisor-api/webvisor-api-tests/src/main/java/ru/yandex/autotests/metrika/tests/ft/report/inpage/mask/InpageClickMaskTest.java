package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.Map;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.data.inpage.Click;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.autotests.metrika.utils.Utils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.is;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.CLICK, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Карта кликов. Маски url")
public class InpageClickMaskTest {

    private static UserSteps user = new UserSteps();

    private MapsV1DataClickGETSchema resultShipping;
    private MapsV1DataClickGETSchema resultPayment;
    private MapsV1DataClickGETSchema resultCart;
    private MapsV1DataClickGETSchema resultShippingPayment;

    private Map<String, Set<Click>> shippingClicks;
    private Map<String, Set<Click>> paymentClicks;
    private Map<String, Set<Click>> shippingPaymentClicks;

    @Before
    public void setup() {
        resultShipping = getResultForUrl(InpageTestData.getShippingUrl());
        resultPayment = getResultForUrl(InpageTestData.getPaymentUrl());
        resultCart = getResultForUrl(InpageTestData.getCartUrl());
        resultShippingPayment = getResultForUrl(InpageTestData.getShippingOrPaymentUrl());

        assumeThat("Данные для cart есть", resultCart.getData().getTotal(), greaterThan(0L));

        shippingClicks = user.onResultSteps().getInpageClickFirstDayClicks(resultShipping);
        paymentClicks = user.onResultSteps().getInpageClickFirstDayClicks(resultPayment);
        shippingPaymentClicks = user.onResultSteps().getInpageClickFirstDayClicks(resultShippingPayment);
        assumeThat("shippingClicks не пустые", shippingClicks.isEmpty(), is(false));
        assumeThat("paymentClicks не пустые", paymentClicks.isEmpty(), is(false));
        assumeThat("shippingPaymentClicks не пустые", shippingPaymentClicks.isEmpty(), is(false));
    }

    @Test
    public void cartIsGreaterEqualThanShippingAndPaymentTotal() {
        assertThat("Totals cart не меньше чем cart/shipping + cart/payment",
                resultCart.getData().getTotal(),
                greaterThanOrEqualTo(resultShipping.getData().getTotal() + resultPayment.getData().getTotal()));
    }

    @Test
    public void cartIsEqualShippingAndPaymentTotal() {
        assertThat("Totals cart/(shipping|payment)/ равно cart/shipping + cart/payment",
                resultShippingPayment.getData().getTotal(),
                equalTo(resultShipping.getData().getTotal() + resultPayment.getData().getTotal()));
    }

    @Test
    public void cartIsEqualShippingAndPayment() {
        Map<String, Set<Click>> shippingAndPaymentClicksZipped = Utils.zip(shippingClicks, paymentClicks);
        assertThat("cart/(shipping|payment)/ равно cart/shipping + cart/payment",
                shippingPaymentClicks,
                equalTo(shippingAndPaymentClicksZipped));
    }

    private MapsV1DataClickGETSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageClickDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
