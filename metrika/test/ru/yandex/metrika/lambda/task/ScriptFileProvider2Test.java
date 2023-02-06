package ru.yandex.metrika.lambda.task;

import org.junit.Test;

import ru.yandex.metrika.lambda.ScriptFileProvider2;
import ru.yandex.metrika.lambda.ScriptFileProviderFixed2;

import static org.junit.Assert.assertEquals;

public class ScriptFileProvider2Test {
    @Test
    public void getScript() throws Exception {
        ScriptFileProvider2 target = new ScriptFileProvider2();
        target.setBefore(new ScriptFileProviderFixed2("before"));
        target.setAfter(new ScriptFileProviderFixed2("after"));
        target.setBoundary("2018-04-16T06:00:00");
        assertEquals("before",target.getScript("2018-04-16T05:00:00"));
        assertEquals("after",target.getScript("2018-04-16T06:00:00"));
        assertEquals("after",target.getScript("2018-04-16T07:00:00"));
    }

}
