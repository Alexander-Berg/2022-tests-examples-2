package ru.yandex.quasar.app.utils;

import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;

import ru.yandex.quasar.util.MetricaUtil;

@RunWith(value = AndroidJUnit4.class)
public class MetricaUtilTest {

    class InnerException extends Exception {
        public InnerException(String message) {
            super(message);
        }
    }

    class OuterException extends Exception {
        public OuterException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    @Test
    public void extractClassesAndMessagesTest() {
        @SuppressWarnings("ThrowableNotThrown")
        final Exception ex = new OuterException("Unknown exception",
                new OuterException("Download failed",
                        new InnerException("Http code 418")));

        final String exceptionsChain = MetricaUtil.extractClassesAndMessages(ex);

        Assert.assertEquals("ru.yandex.quasar.app.utils.MetricaUtilTest$OuterException: Unknown exception" +
                " <- ru.yandex.quasar.app.utils.MetricaUtilTest$OuterException: Download failed" +
                " <- ru.yandex.quasar.app.utils.MetricaUtilTest$InnerException: Http code 418", exceptionsChain);

    }

    @Test
    public void extractClassesAndMessagesNoCauseTest() {
        @SuppressWarnings("ThrowableNotThrown")
        final Exception ex = new OuterException("Http code 418", null);
        final String singleException = MetricaUtil.extractClassesAndMessages(ex);

        Assert.assertEquals("ru.yandex.quasar.app.utils.MetricaUtilTest$OuterException: Http code 418", singleException);
    }

}
