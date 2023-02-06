package ru.yandex.metrika.mobmet.crash.decoder.service.ios.group;

import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class ErrorMessageTrimmerTest {

    private ErrorMessageTrimWordsDao dao = mock(ErrorMessageTrimWordsDao.class);
    private ErrorMessageTrimmer nameTrimmer = new ErrorMessageTrimmer(dao);

    @Before
    public void before() {
        when(dao.getWords()).thenReturn(List.of(
                new ErrorMessageTrimWord(13, "for login"),
                new ErrorMessageTrimWord(13, "account")
        ));
        nameTrimmer.init();
    }

    @Test
    public void testNormal() {
        String actual = nameTrimmer.trim(13, "NSException");
        Assert.assertEquals("NSException", actual);
    }

    @Test
    public void testNormalWithSpecialCharacters() {
        String actual = nameTrimmer.trim(13, "MetricaSample.SomeError.some_case");
        Assert.assertEquals("MetricaSample.SomeError.some_case", actual);
    }

    @Test
    public void testTrimWithSpecialCharacters() {
        String actual = nameTrimmer.trim(13, "MetricaSample.SomeError.some_case(message: \"Some message\")");
        Assert.assertEquals("MetricaSample.SomeError.some_case(message: \"Some...", actual);
    }

    @Test
    public void testBigMessage() {
        String actual = nameTrimmer.trim(13, "RCTFatalException: Unhandled JS Exception: scrollToIndex out of range: -1 vs 19");
        Assert.assertEquals("RCTFatalException: Unhandled JS Exception:...", actual);
    }

    @Test
    public void testRulesForSmallMessage() {
        String actual = nameTrimmer.trim(13, "test for login account and best word");
        Assert.assertEquals("test for login...", actual);
    }

    @Test
    public void testRulesForBigMessage() {
        String actual = nameTrimmer.trim(13, "RCTFatalException: Unhandled account JS Exception: scrollToIndex out of range: -1 vs 19");
        Assert.assertEquals("RCTFatalException: Unhandled account...", actual);
    }
}
