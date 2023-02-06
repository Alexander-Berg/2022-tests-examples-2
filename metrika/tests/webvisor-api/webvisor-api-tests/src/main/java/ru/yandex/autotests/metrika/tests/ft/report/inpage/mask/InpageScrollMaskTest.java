package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
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
@Stories({Requirements.Story.Inpage.SCROLL, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Карта скроллов. Маски url")
public class InpageScrollMaskTest {
    private static UserSteps user = new UserSteps();

    private List<Long> shippingPlusPaymentScrolls;
    private List<Long> shippingAndPaymentScrolls;
    private List<Long> cartScrolls;
    private List<Long> shippingScrolls;
    private List<Long> paymentScrolls;

    @Before
    public void setup() {
        MapsV1DataScrollGETSchema resultShipping = getResultForUrl(InpageTestData.getShippingUrl());
        MapsV1DataScrollGETSchema resultPayment = getResultForUrl(InpageTestData.getPaymentUrl());
        MapsV1DataScrollGETSchema resultCart = getResultForUrl(InpageTestData.getCartUrl());
        MapsV1DataScrollGETSchema resultShippingAndPayment = getResultForUrl(InpageTestData.getShippingOrPaymentUrl());

        cartScrolls = resultCart.getData();
        shippingAndPaymentScrolls = resultShippingAndPayment.getData();
        shippingScrolls = resultShipping.getData();
        paymentScrolls = resultPayment.getData();

        assumeThat("Данные для cart есть", cartScrolls, not(empty()));
        assumeThat("Данные для shipping есть", shippingScrolls, not(empty()));
        assumeThat("Данные для payment есть", paymentScrolls, not(empty()));
        assumeThat("Данные для shippingAndPayment есть", shippingAndPaymentScrolls, not(empty()));

        shippingPlusPaymentScrolls = user.onResultSteps().scrollsPlus(shippingScrolls, paymentScrolls);
    }

    @Test
    public void cartIsGreaterEqualThanShippingAndPayment() {
        assertThat("Data cart - (cart/shipping + cart/payment) не меньше чем 0",
                user.onResultSteps().scrollsMinus(cartScrolls, shippingAndPaymentScrolls),
                everyItem(greaterThanOrEqualTo(0L)));
    }

    @Test
    public void cartIsEqualShippingAndPayment() {

        assertThat("Data cart/(shipping|payment)/ - (cart/shipping + cart/payment) равно 0",
                user.onResultSteps().scrollsMinus(shippingAndPaymentScrolls, shippingPlusPaymentScrolls),
                everyItem(equalTo(0L)));
    }

    private MapsV1DataScrollGETSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageScrollDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
