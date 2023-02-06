package ru.yandex.metrika.util.mail;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.Level;
import org.joda.time.DateTime;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.mockito.Matchers;

import ru.yandex.metrika.api.management.client.AddGrantRequest;
import ru.yandex.metrika.api.management.client.external.DelegateRequestE;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mail.FreemarkerRenderer;
import ru.yandex.metrika.mail.Message;
import ru.yandex.metrika.mail.MessageQueue;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.metrika.util.app.Settings;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.misc.email.Email;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * проверка текстов шаблонов писем отправляемых из интерфейса.
 * Created with IntelliJ IDEA.
 * User: temld4
 * Date: 11/28/13
 * Time: 7:02 PM
 * To change this template use File | Settings | File Templates.
 */
public class MailGeneratorTest {
    private static final long NOW = 1385654413883L;
    private static final int UID = 41;
    private MailGenerator target;
    private AuthUtils authUtils;
    MessageQueue mq = mock(MessageQueue.class);

    @Before
    public void setUp() throws Exception {
        System.setProperty(Settings.ENV_PROPERTY, "development");
        Log4jSetup.basicSetup(Level.DEBUG);
        target = new MailGenerator();
        //mailGenerator.setTemplates(MailGenerator.getTemplates("faced/src/java/ru/yandex/metrika/util/mail/templates/grants/grant-request-letter.stg"));
        LocaleDictionaries ld = new LocaleDictionaries();
        ld.afterPropertiesSet();
        target.setLocaleDictionaries(ld);
        FreemarkerRenderer render = new FreemarkerRenderer();
        render.setLoaderClass(target.getClass());
        render.afterPropertiesSet();
        target.setRender(render);
        when(mq.insert(Matchers.<Message>anyObject())).thenReturn(1);
        target.setMessageQueue(mq);
        target.setTimeProvider(Clock.fixed(Instant.ofEpochMilli(NOW), ZoneId.systemDefault()));
        authUtils = new AuthUtils();
        /*        AuthUtils authUtils = mock(AuthUtils.class);
                when(authUtils.authByUid(eq(UID))).thenReturn(AuthUtils.buildFakeDetails(UID, true, "127.0.0.1"));
                when(authUtils.authByLogin(anyString())).thenReturn(AuthUtils.buildFakeDetails(UID2, true, "127.0.0.1"));
                //AuthUtils authUtils = new AuthUtils();
                FrontendSettings settings = new FrontendSettings();
                //settings.setBlackboxUrl("http://metrika-dev.yandex.ru:8788/blackbox");
        */
        authUtils.setBlackboxUrl("http://metrika-dev.haze.yandex.ru:8788/blackbox");
        authUtils.afterPropertiesSet();
        target.setAuthUtils(authUtils);
        target.afterPropertiesSet();
    }

    @Test
    @Ignore("METRIQA-936")
    public void testGrantRequestLetter() {
        // [{"lang":"ru","object_type":"site","send_email":"f1nalTest4@yandex.ru","permission":"RO","send_sms":0,"service_name":"direct",
        // "comment":"ppalex","object_id":"pets.nwcode.ru","owner_login":"n1server","requestor_login":"f1nalTest4"}]"
        AddGrantRequest request = new AddGrantRequest();
        request.setLang("ru");
        request.setObjectType(AddGrantRequest.AddRequestType.counter);
        request.setSendEmail("f1nalTest4@yandex.ru");
        request.setPermission("RO");
        request.setSendSms(0);
        request.setServiceName("direct");
        request.setComment("ppalex");
        request.setObjectId("123456789");
        request.setOwnerLogin("n1server");
        request.setRequestorLogin("f1nalTest4");

        List<AddGrantRequest> requests = new ArrayList<>();
        requests.add(request);
        target.grantRequestLetter(UID, new Email("peter@petrov.ru"), "peter petrov", requests, "ru");
        ///////////////////////////////////
        Message standardMessage = new Message();
        standardMessage.setUid(UID);
        standardMessage.setAddTime(new DateTime(NOW));
        standardMessage.setExpectedSendTime(new DateTime(NOW));
        standardMessage.setTemplateName("grant_request");
        standardMessage.setMessage(
           "Subject: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCwOiDQt9Cw0L/RgNC+0YEg0LTQvtGB0YLRg9C/0LA=?=\n" +
           "Precedence: bulk\n" +
           "From: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCw?=<devnull@yandex.ru>\n" +
           "To: peter@petrov.ru\n" +
           "Content-Type: text/plain; charset=\"utf-8\"\n" +
           "Content-Transfer-Encoding: 8bit\n" +
           "Mime-Version: 1.0\n" +
                   '\n' +
           "Здравствуйте, peter petrov!\n" +
                   '\n' +
           "Пользователь f1nalTest4 запрашивает доступ к вашему счетчику Метрики № 123456789.\n" +
           "Для подтверждения или отклонения доступа перейдите, пожалуйста, по ссылке https://metrika.yandex.ru/123456789?tab=grants\n" +
           "Вы можете установить для этого пользователя уровень доступа по вашему выбору (только на просмотр или полный доступ).\n" +
           "--\n" +
           "С уважением,\n" +
           "Яндекс.Метрика\n" +
           "https://yandex.ru/support/metrika/\n" +
           "https://metrika.yandex.ru");
        verify(mq).insert(standardMessage);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testGrantRequestAllowLetter() {
        target.grantRequestResultLetter(101500, "Яндекс.Директ", "ppalex", UID, LocaleLangs.getDefaultLang(), true, Permission.edit);
        ///////////////////////////////////
        Message standardMessage = new Message();
        standardMessage.setUid(29230599);
        standardMessage.setAddTime(new DateTime(NOW));
        standardMessage.setExpectedSendTime(new DateTime(NOW));
        standardMessage.setTemplateName("grant_counter_result");
        standardMessage.setMessage(
      "Subject: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCwOiDQtNC+0YHRgtGD0L8g0L/QvtC00YLQstC10YDQttC00LXQvQo=?=\n" +
      "Date: Thu, 28 Nov 2013 20:00:13 +0400\n" +
      "X-Yandex-Service: eWFtZXRyaWthIO+/ve+/vWrKrHnvv73Duwhw77+9HkXvv73vv70=\n" +
      "Precedence: bulk\n" +
      "From: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCw?=<devnull@yandex.ru>\n" +
      "To: PPAlex@yandex.ru\n" +
       "Content-Type: text/plain; charset=\"utf-8\"\n" +
       "Content-Transfer-Encoding: 8bit\n" +
       "Mime-Version: 1.0\n" +
              '\n' +
       "Здравствуйте, Pupkin Vasily!\n" +
              '\n' +
       "Пользователь volozh подтвердил ваш запрос на доступ к своему счетчику № 101500 - вам выдан полный доступ.\n" +
      "Теперь вы можете использовать цели, заданные на этом счетчике, для настроек кампаний Яндекс.Директ.\n" +
              '\n' +
       "--\n" +
       "С уважением,\n" +
       "Яндекс.Метрика\n" +
       "https://yandex.ru/support/metrika/\n" +
       "https://metrika.yandex.ru");
        verify(mq).insert(standardMessage);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testGrantRequestDenyLetter() {
        target.grantRequestResultLetter(101500, "direct", "ppalex", UID, LocaleLangs.getDefaultLang(), false, Permission.edit);
        ///////////////////////////////////
        Message standardMessage = new Message();
        standardMessage.setUid(29230599);
        standardMessage.setAddTime(new DateTime(NOW));
        standardMessage.setExpectedSendTime(new DateTime(NOW));
        standardMessage.setTemplateName("grant_counter_result");
        standardMessage.setMessage(
      "Subject: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCwOiDQtNC+0YHRgtGD0L8g0L7RgtC60LvQvtC90LXQvQo=?=\n" +
      "Date: Thu, 28 Nov 2013 20:00:13 +0400\n" +
      "X-Yandex-Service: eWFtZXRyaWthIO+/vV3vv73vv73vv73vv73vv71I77+9Ke+/vUXvv73vv73EmA==\n" +
      "Precedence: bulk\n" +
      "From: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCw?=<devnull@yandex.ru>\n" +
      "To: PPAlex@yandex.ru\n" +
      "Content-Type: text/plain; charset=\"utf-8\"\n" +
      "Content-Transfer-Encoding: 8bit\n" +
      "Mime-Version: 1.0\n" +
              '\n' +
      "Здравствуйте, Pupkin Vasily!\n" +
              '\n' +
      "К сожалению, пользователь volozh отклонил ваш запрос на доступ к своему счетчику № 101500.\n" +
              '\n' +
      "--\n" +
      "С уважением,\n" +
              "Яндекс.Метрика\n" +
       "https://yandex.ru/support/metrika/\n" +
       "https://metrika.yandex.ru");
        verify(mq).insert(standardMessage);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testDelegateRequestAllowLetter() {
        DelegateRequestE form = new DelegateRequestE();
        MetrikaUserDetails targetUser = authUtils.authByLogin("volozh");
        form.setComment("ppalex");
        form.setUserLogin("ppalex");   // unknownLogin throws exception.
        form.setVote(true);
        target.grantRequestResultLetter(targetUser, form, LocaleLangs.getDefaultLang());
        ///////////////////////////////////
        Message standardMessage = new Message();
        standardMessage.setUid(29230599);
        standardMessage.setAddTime(new DateTime(NOW));
        standardMessage.setExpectedSendTime(new DateTime(NOW));
        standardMessage.setTemplateName("grant_account_result");
        standardMessage.setMessage(
      "Subject: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCwOiDQtNC+0YHRgtGD0L8g0L/QvtC00YLQstC10YDQttC00LXQvQ==?=\n" +
      "Date: Thu, 28 Nov 2013 20:00:13 +0400\n" +
      "X-Yandex-Service: eWFtZXRyaWthIO+/vTfvv73vv73vv73vv73vv717ZFh3KRXvv70oVQ==\n" +
      "Precedence: bulk\n" +
      "From: =?utf-8?B?0K/QvdC00LXQutGBLtCc0LXRgtGA0LjQutCw?=<devnull@yandex.ru>\n" +
      "To: PPAlex@yandex.ru\n" +
       "Content-Type: text/plain; charset=\"utf-8\"\n" +
       "Content-Transfer-Encoding: 8bit\n" +
       "Mime-Version: 1.0\n" +
              '\n' +
       "Здравствуйте, Pupkin Vasily!\n" +
              '\n' +
       "Пользователь volozh подтвердил ваш запрос на представительский доступ к своему аккаунту Яндекс.Метрики.\n" +
              "Теперь вы имеете полный доступ ко всем счетчикам данного аккаунта.\n" +
              '\n' +
       "--\n" +
       "С уважением,\n" +
       "Яндекс.Метрика\n" +
       "https://yandex.ru/support/metrika/\n" +
       "https://metrika.yandex.ru");
        verify(mq).insert(standardMessage);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testGrantRequestAllowSms() {
        target.grantRequestResultSms(101500, "ppalex", UID, LocaleLangs.getDefaultLang(), true);
        ///////////////////////////////////
        Message standardMessage = new Message();
        standardMessage.setUid(29230599);
        standardMessage.setSms(true);
        standardMessage.setAddTime(new DateTime(NOW));
        standardMessage.setExpectedSendTime(new DateTime(NOW));      // !!!!! TODO  время должно быть хорошее
        standardMessage.setTemplateName("grant_counter_result");
        standardMessage.setMessage(
          "Пользователь volozh подтвердил ваш запрос на доступ к счетчику Яндекс.Метрики № 101500");
        verify(mq).insert(standardMessage);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testGrantRequestDenySms() {
        target.grantRequestResultSms(101500, "ppalex", UID, LocaleLangs.getDefaultLang(), false);
        ///////////////////////////////////
        Message standardMessage = new Message();
        standardMessage.setUid(29230599);
        standardMessage.setSms(true);
        standardMessage.setAddTime(new DateTime(NOW));
        standardMessage.setExpectedSendTime(new DateTime(NOW));   // !!!!! TODO  время должно быть хорошее
        standardMessage.setTemplateName("grant_counter_result");
        standardMessage.setMessage(
          "Пользователь volozh отклонил ваш запрос на доступ к счетчику Яндекс.Метрики № 101500");
        verify(mq).insert(standardMessage);
    }


    /*@Test
    public void testTemplate() {
        target.buildMessage(42, "anc", new HashMap<>(), "macro_test", "ru");
    }
*/










}
