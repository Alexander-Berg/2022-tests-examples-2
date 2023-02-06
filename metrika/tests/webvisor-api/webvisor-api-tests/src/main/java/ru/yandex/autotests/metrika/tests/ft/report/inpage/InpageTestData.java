package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;

public class InpageTestData {

    private static Counter counter = CounterConstants.LITE_DATA;

    private static final String INPAGE_START_DATE = "14daysAgo";
    private static final String INPAGE_END_DATE = "7daysAgo";
    private static final int HEIGHT = 100;

    private static final String SHIPPING_URL = "*https://sendflowers.ru/cart/shipping/*";
    private static final String PAYMENT_URL = "*https://sendflowers.ru/cart/payment/*";
    private static final String CART_URL = "*https://sendflowers.ru/cart/*";
    private static final String SHIPPING_OR_PAYMENT_URL = "~^https://sendflowers.ru/cart/(shipping|payment)/";
    private static final String REGEX_URL = "~^https://sendflowers.ru/rus/\\w+-russia-[mscow]+$";

    public static String getInpageStartDate() {
        return INPAGE_START_DATE;
    }

    public static String getInpageEndDate() {
        return INPAGE_END_DATE;
    }

    public static int getHeight() {
        return HEIGHT;
    }

    public static String getShippingUrl() {
        return SHIPPING_URL;
    }

    public static String getPaymentUrl() {
        return PAYMENT_URL;
    }

    public static String getCartUrl() {
        return CART_URL;
    }

    public static String getShippingOrPaymentUrl() {
        return SHIPPING_OR_PAYMENT_URL;
    }

    public static String getRegexUrl() {
        return REGEX_URL;
    }

    public static CommonReportParameters getReportParameters(String url) {
        return new InpageDataParameters()
                .withId(counter)
                .withDate1(InpageTestData.getInpageStartDate())
                .withDate2(InpageTestData.getInpageEndDate())
                .withHeight(String.valueOf(InpageTestData.getHeight()))
                .withUrl(url);
    }
}
