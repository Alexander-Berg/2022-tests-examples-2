package ru.yandex.metrika.api.constructor.contr;

import java.util.Date;

import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.context.support.ClassPathXmlApplicationContext;
import org.springframework.mock.http.MockHttpOutputMessage;

import ru.yandex.metrika.api.constructor.presets.PresetExternal;
import ru.yandex.metrika.api.constructor.presets.PresetService;
import ru.yandex.metrika.api.constructor.segment.PresetsController;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.spring.JacksonViewMessageConverter;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;
import ru.yandex.metrika.spring.response.ResponseWrapper;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

@Ignore
public class PresetsControllerTest {

    private PresetsController target;
    private JacksonViewMessageConverter converter;
    private ClassPathXmlApplicationContext context;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        context = new ClassPathXmlApplicationContext("/ru/yandex/metrika/ui/constructor/contr/faced-test.xml");
        target = new PresetsController();
        PresetService presetService =  context.getBean(PresetService.class);
        target.setPresetService(presetService);
        converter = new MetrikaApiMessageConverter();
    }

    @Test
    public void testGetPreset() throws Exception {
        // http://localhost:8082/secure/api/preset.json?name=traffic&with_tree=1&uid_real=22892801&uid=22892801&lang=ru'
        {
            MetrikaUserDetails user = AuthUtils.ANON;
            AuthUtils.setUserDetails(user);
            for (int i = 0; i < 10; i++) {
                ResponseWrapper<PresetExternal> resp = target.getPreset("traffic", LocaleLangs.getDefaultLang()).call();
                MockHttpOutputMessage outputMessage = new MockHttpOutputMessage();
                converter.write(resp, converter.getSupportedMediaTypes().get(0), outputMessage);
            }
        }
        System.out.println("new Date() = " + new Date());
        for (int i = 0; i < 50; i++) {
            long start = System.nanoTime();
            MetrikaUserDetails user = AuthUtils.ANON;
            AuthUtils.setUserDetails(user);
            ResponseWrapper<PresetExternal> resp = target.getPreset("traffic", LocaleLangs.getDefaultLang()).call();
            MockHttpOutputMessage outputMessage = new MockHttpOutputMessage();
            converter.write(resp, converter.getSupportedMediaTypes().get(0), outputMessage);
            long end = System.nanoTime();
            System.out.println("System.nanoTime() = " + (end -start) + '\n' +outputMessage.getBodyAsString());
        }
    }
}
