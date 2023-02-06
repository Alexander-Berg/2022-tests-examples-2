package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.List;
import java.util.Map;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasValue;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.LINK, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Карта ссылок. Маски url")
public class InpageLinkMaskTest {
    private static UserSteps user = new UserSteps();

    private MapsV1DataLinkMapGETSchema resultShipping;
    private MapsV1DataLinkMapGETSchema resultPayment;
    private MapsV1DataLinkMapGETSchema resultCart;
    private MapsV1DataLinkMapGETSchema resultShippingAndPayment;

    private Map<String, List<Integer>> shippingLinks;
    private Map<String, List<Integer>> paymentLinks;
    private Map<String, List<Integer>> cartLinks;
    private Map<String, List<Integer>> shippingAndPaymentLinks;
    private Map<String, List<Integer>> shippingPlusPaymentLinks;


    @Before
    public void setup() {
        resultShipping = getResultForUrl(InpageTestData.getShippingUrl());
        resultPayment = getResultForUrl(InpageTestData.getPaymentUrl());
        resultCart = getResultForUrl(InpageTestData.getCartUrl());
        resultShippingAndPayment = getResultForUrl(InpageTestData.getShippingOrPaymentUrl());

        shippingLinks = resultShipping.getData().getL();
        paymentLinks = resultPayment.getData().getL();
        cartLinks = resultCart.getData().getL();
        shippingAndPaymentLinks = resultShippingAndPayment.getData().getL();

        assumeThat("Данные для cart есть", cartLinks.keySet(), not(empty()));
        assumeThat("Данные для shipping есть", shippingLinks.keySet(), not(empty()));
        assumeThat("Данные для payment есть", paymentLinks.keySet(), not(empty()));
        assumeThat("Данные для shippingAndPayment есть", shippingAndPaymentLinks.keySet(), not(empty()));

        shippingPlusPaymentLinks = user.onResultSteps().linksPlus(shippingLinks, paymentLinks);
    }

    @Test
    public void cartIsGreaterEqualThanShippingAndPayment() {
        assertThat("cart минус cart/shipping + cart/payment не меньше 0",
                user.onResultSteps().linksMinus(cartLinks, shippingPlusPaymentLinks),
                not(hasValue(hasValue(lessThan(0)))));
    }

    @Test
    public void cartIsEqualShippingAndPayment() {
        assertThat("cart/(shipping|payment)/ минус cart/shipping + cart/payment равно 0",
                user.onResultSteps().linksMinus(shippingAndPaymentLinks, shippingPlusPaymentLinks).values(),
                everyItem(everyItem(equalTo(0))));
    }

    private MapsV1DataLinkMapGETSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageLinkDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
