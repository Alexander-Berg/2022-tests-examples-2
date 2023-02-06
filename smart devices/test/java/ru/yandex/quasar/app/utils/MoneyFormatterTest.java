package ru.yandex.quasar.app.utils;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import java.math.BigDecimal;
import java.util.Locale;

public class MoneyFormatterTest {

    private Locale defaultLocale = null;
    @Before
    public void setUp() {
        defaultLocale = Locale.getDefault();
        Locale locale = new Locale("ru");
        Locale.setDefault(locale);
    }

    @Test
    public void testMoneyFormatter() {
        Assert.assertEquals("23,33", Utils.formatMoney(new BigDecimal("23.33")));
        Assert.assertEquals("23,33", Utils.formatMoney(new BigDecimal("23.332")));
        Assert.assertEquals("23,33", Utils.formatMoney(new BigDecimal("23.330")));
        Assert.assertEquals("23,30", Utils.formatMoney(new BigDecimal("23.30")));
        Assert.assertEquals("23,30", Utils.formatMoney(new BigDecimal("23.3")));
        Assert.assertEquals("23", Utils.formatMoney(new BigDecimal("23.0")));
        Assert.assertEquals("23", Utils.formatMoney(new BigDecimal("23")));
        Assert.assertEquals("23", Utils.formatMoney(new BigDecimal("23.001")));
        Assert.assertEquals("1234", Utils.formatMoney(new BigDecimal("1233.999")));
        Assert.assertEquals("1233,99", Utils.formatMoney(new BigDecimal("1233.989")));
    }

    @After
    public void tearDown() {
        Locale.setDefault(defaultLocale);
    }
}
