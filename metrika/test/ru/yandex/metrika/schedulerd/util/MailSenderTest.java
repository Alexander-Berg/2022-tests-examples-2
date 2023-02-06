package ru.yandex.metrika.schedulerd.util;

import java.util.Properties;
import java.util.TreeMap;
import java.util.TreeSet;

import junit.framework.Assert;
import org.apache.logging.log4j.Level;
import org.joda.time.DateTime;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;
import ru.yandex.metrika.mail.Message;
import ru.yandex.metrika.mail.MessageQueue;
import ru.yandex.metrika.schedulerd.cron.task.NotificationTask;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * без LANG компиляция падает на файле Костыля. до теста дело так сказать не совсем доходит.
 * ssh -L 1025:localhost:25 mtbot1.yandex.ru
 * @author orantius
 * @version $Id$
 * @since 1/31/14
 */
public class MailSenderTest {

    private NotificationTask target;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        target = new NotificationTask();
        target.setSmtpHost("localhost");
        target.setSmtpPort(1025);
        target.setMessageQueue(new MessageQueue());
        TreeMap<String, String> env = new TreeMap<>(System.getenv());
        env.keySet().stream().forEach(p-> System.out.println(p+" = " + env.get(p)));
        System.out.println();
        System.out.println();
        Properties ps = System.getProperties();
        new TreeSet<String>(ps.stringPropertyNames()).stream().forEach(p-> System.out.println(p+" = " + ps.getProperty(p)));
    }

    @Test
    @Ignore
    public void testSendLetter() throws Exception {
        Message message = new Message();
        message.setMessage(
                "Subject: =?utf-8?B?QWNjb3VudCBncmFudCByZXF1ZXN0?=\n" +
                "Date: Thu, 28 Nov 2013 20:00:13 +0400\n" +
                "X-Yandex-Service: eWFtZXRyaWthIEjvv73Ip++/ve+/vTZL77+9xZpv77+9CBI7\n" +
                "Precedence: bulk\n" +
                "From: =?utf-8?B?ZGV2bnVsbEB5YW5kZXgucnU=?=<devnull@yandex.ru>\n" +
                "To: orantius@yandex-team.ru\n" +
                "ContentType: text/plain; charset=\"utf-8\"\n" +
                "ContentTransferEncoding: 8bit\n" +
                "MimeVersion: 1.0\n" +
                '\n' +
                "Здравствуйте, Pupkin Vasily!\n" +
                '\n' +
                "Пользователь volozh подтвердил ваш запрос на представительский доступ к своему аккаунту Яндекс.Метрики.\n" +
                "Теперь вы имеете полный доступ ко всем счетчикам данного аккаунта.\n" +
                "--\n" +
                "С уважением,\n" +
                "\"Яндекс.Метрика\"\n" +
                "http://feedback.yandex.ru/?from=metrika\n" +
                "http://metrika.yandex.ru\n" +
                "тел.: (495) 739-22-22 (по будням с 9:00 до 19:00)\n" +
                "тел.: (800) 333-96-39 (по будням с 9:00 до 19:00, звонок из регионов России бесплатный)"
        );
        Assert.assertTrue(target.sendLetter(message));
    }

    @Test(timeout = 5000)
    @Ignore
    public void testSendSms() throws Exception {
        Message message = new Message();
        message.setUid(30127817 /* чей-нибудь uid*/);
        message.setMessage("test message");
        Assert.assertTrue(target.sendSms(message));
    }

    /**
     * ssh -L 3306:localhost:3306 mtweb02t
     * ssh -L 25:localhost:25 mtbot1
     */
    @Test
    @Ignore
    public void testExpire() throws Exception {
        TransactionalMetrikaDataSource dataSource = new DataSourceFactory().getDataSource();
        dataSource.setHost("127.0.0.1");
        dataSource.setPort(3307);
        dataSource.setUser("root");
        dataSource.setDb("monitoring");
        dataSource.afterPropertiesSet();

        DateTime now = new DateTime();

        Message message = new Message();
        message.setUid(30127817 /* чей-нибудь uid*/);
        message.setAddTime(now);
        message.setExpectedSendTime(now);
        message.setTemplateName("site");
        message.setMessage("test message");
        message.setPhone("79169069311");

        MessageQueue messageQueue = new MessageQueue();
        messageQueue.setTemplate(new MySqlJdbcTemplate(dataSource));
        messageQueue.insert(message);

        NotificationTask sender = new NotificationTask();
        sender.setMessageQueue(messageQueue);
        sender.setMaxLetterQueueSize(0);
        sender.setMaxSmsQueueSize(0);
        sender.send();
    }
}
/*
окружение курильщика.
CLASSPATH = /home/orantius/dev/idea-IU-139.224.1/bin/../lib/bootstrap.jar:/home/orantius/dev/idea-IU-139.224.1/bin/../lib/extensions.jar:/home/orantius/dev/idea-IU-139.224.1/bin/../lib/util.jar:/home/orantius/dev/idea-IU-139.224.1/bin/../lib/jdom.jar:/home/orantius/dev/idea-IU-139.224.1/bin/../lib/log4j.jar:/home/orantius/dev/idea-IU-139.224.1/bin/../lib/trove4j.jar:/home/orantius/dev/idea-IU-139.224.1/bin/../lib/jna.jar:/usr/local/jdk1.8.0_08/lib/tools.jar
CLUTTER_IM_MODULE = xim
COLORTERM = gnome-terminal
COMPIZ_CONFIG_PROFILE = ubuntu
DBUS_SESSION_BUS_ADDRESS = unix:abstract=/tmp/dbus-XnqSCmXbVD
DEBEMAIL = orantius@yandex-team.ru
DEBFULLNAME = Yuriy Galitskiy
DEFAULTS_PATH = /usr/share/gconf/ubuntu.default.path
DESKTOP_SESSION = ubuntu
DISPLAY = :0
GDMSESSION = ubuntu
GDM_LANG = en_US
GNOME_DESKTOP_SESSION_ID = this-is-deprecated
GNOME_KEYRING_CONTROL = /run/user/1000/keyring-xI06LK
GNOME_KEYRING_PID = 1972
GPG_AGENT_INFO = /run/user/1000/keyring-xI06LK/gpg:0:1
GTK_IM_MODULE = ibus
GTK_MODULES = overlay-scrollbar:unity-gtk-module
HOME = /home/orantius
IM_CONFIG_PHASE = 1
INSTANCE = Unity
JOB = gnome-session
LANG = en_US.UTF-8
LANGUAGE = en_US
LD_LIBRARY_PATH = /home/orantius/dev/idea-IU-139.224.1/bin:
LESSCLOSE = /usr/bin/lesspipe %s %s
LESSOPEN = | /usr/bin/lesspipe %s
LOGNAME = orantius
LS_COLORS = rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lz=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.axv=01;35:*.anx=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.axa=00;36:*.oga=00;36:*.spx=00;36:*.xspf=00;36:
MANDATORY_PATH = /usr/share/gconf/ubuntu.mandatory.path
NLSPATH = /usr/dt/lib/nls/msg/%L/%N.cat
PATH = /home/orantius/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
PWD = /home/orantius
QT4_IM_MODULE = xim
QT_QPA_PLATFORMTHEME = appmenu-qt5
SELINUX_INIT = YES
SESSIONTYPE = gnome-session
SHELL = /bin/bash
SHLVL = 1
SSH_AGENT_LAUNCHER = upstart
SSH_AGENT_PID = 2043
SSH_AUTH_SOCK = /run/user/1000/keyring-xI06LK/ssh
TERM = xterm
TEXTDOMAIN = im-config
TEXTDOMAINDIR = /usr/share/locale/
UBUNTU_MENUPROXY = 1
UPSTART_EVENTS = started starting
UPSTART_INSTANCE =
UPSTART_JOB = unity-settings-daemon
UPSTART_SESSION = unix:abstract=/com/ubuntu/upstart-session/1000/1974
USER = orantius
VTE_VERSION = 3409
WINDOWID = 46152353
XAUTHORITY = /home/orantius/.Xauthority
XDG_CONFIG_DIRS = /etc/xdg/xdg-ubuntu:/usr/share/upstart/xdg:/etc/xdg
XDG_CURRENT_DESKTOP = Unity
XDG_DATA_DIRS = /usr/share/ubuntu:/usr/share/gnome:/usr/local/share/:/usr/share/
XDG_GREETER_DATA_DIR = /var/lib/lightdm-data/orantius
XDG_RUNTIME_DIR = /run/user/1000
XDG_SEAT = seat0
XDG_SEAT_PATH = /org/freedesktop/DisplayManager/Seat0
XDG_SESSION_ID = c2
XDG_SESSION_PATH = /org/freedesktop/DisplayManager/Session0
XDG_VTNR = 7
XFILESEARCHPATH = /usr/dt/app-defaults/%L/Dt
XMODIFIERS = @im=ibus
_ = /home/orantius/dev/idea-IU-139.224.1/bin/idea.sh

awt.toolkit = sun.awt.X11.XToolkit
file.encoding = UTF-8
file.encoding.pkg = sun.io
file.separator = /
java.awt.graphicsenv = sun.awt.X11GraphicsEnvironment
java.awt.printerjob = sun.print.PSPrinterJob
java.class.path = /home/orantius/dev/idea-IU-139.224.1/lib/idea_rt.jar:/home/orantius/dev/idea-IU-139.224.1/plugins/junit/lib/junit-rt.jar:/usr/lib/jvm/java-8-oracle/jre/lib/javaws.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jfr.jar:/usr/lib/jvm/java-8-oracle/jre/lib/rt.jar:/usr/lib/jvm/java-8-oracle/jre/lib/resources.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jsse.jar:/usr/lib/jvm/java-8-oracle/jre/lib/deploy.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jce.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jfxswt.jar:/usr/lib/jvm/java-8-oracle/jre/lib/management-agent.jar:/usr/lib/jvm/java-8-oracle/jre/lib/charsets.jar:/usr/lib/jvm/java-8-oracle/jre/lib/plugin.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/localedata.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/sunjce_provider.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/nashorn.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/sunpkcs11.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/jfxrt.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/dnsns.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/cldrdata.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/zipfs.jar:/usr/lib/jvm/java-8-oracle/jre/lib/ext/sunec.jar:/home/orantius/dev/projects/metrika/metrika-api/out/test/schedulerd:/home/orantius/dev/projects/metrika/metrika-api/out/production/schedulerd:/home/orantius/dev/projects/metrika/metrika-api/out/test/common:/home/orantius/dev/projects/metrika/metrika-api/out/production/common:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/gtree-0.66.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/dom4j-1.6.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jaxen-1.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/libidn-1.15.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/guava-13.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/args4j-2.0.21.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/trove4j-3.0.3.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/java-ipv6-0.15.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/msgpack-0.6.11.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/aopalliance-1.0.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/json-simple-1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/slf4j-api-1.7.5.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/annotations-13.0.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/commons-lang-2.6.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/joda-convert-1.6.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/metrics-jvm-3.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jackson-core-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jul-to-slf4j-1.7.5.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/metrics-core-3.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/aspectjweaver-1.7.4.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/commons-lang3-3.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/javassist-3.18.1-GA.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/bolts-20140311120724.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/commons-logging-1.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jackson-databind-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jboss-logging-3.1.4.GA.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/metrics-graphite-3.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/commons-beanutils-1.9.2.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/joda-time-2.4.tz-patched.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/metrics-annotation-3.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/spring-aop-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/spring-web-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jackson-annotations-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/spring-core-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/metrics-healthchecks-3.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/spring-beans-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/jmxremote_optional-1.0.1_04.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/metrics-spring-3.0.2.PATCHED.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/spring-context-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/spring-expression-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/default/misc-r20140530141418.57835fd6eeeb.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/test/junit-4.8.2.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/test/mockito-all-1.8.5.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/test/spring-test-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/common/lib/test/commons-collections-testframework-3.1.jar:/home/orantius/dev/projects/metrika/metrika-api/common/locale/bundles:/home/orantius/dev/projects/metrika/metrika-api/out/production/passport:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/asm-all-5.0.3.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/httpcore-4.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/httpmime-4.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/servlet-api-3.0.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/stax2-api-3.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/httpclient-4.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/woodstox-core-asl-4.1.4.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/spring-webmvc-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/spring-security-web-3.1.4.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/spring-security-core-3.1.4.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/inside-r20140530141418.57835fd6eeeb.jar:/home/orantius/dev/projects/metrika/metrika-api/passport/lib/default/spring-security-config-3.1.4.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/out/test/frontend-common:/home/orantius/dev/projects/metrika/metrika-api/out/production/frontend-common:/home/orantius/dev/projects/metrika/metrika-api/out/test/segments:/home/orantius/dev/projects/metrika/metrika-api/out/production/segments:/home/orantius/dev/projects/metrika/metrika-api/segments/lib/default/commons-math3-3.4.1.jar:/home/orantius/dev/projects/metrika/metrika-api/segments/lib/default/commons-beanutils-1.9.2.jar:/home/orantius/dev/projects/metrika/metrika-api/out/test/webvisor-common:/home/orantius/dev/projects/metrika/metrika-api/out/production/webvisor-common:/home/orantius/dev/projects/metrika/metrika-api/out/test/dbclients:/home/orantius/dev/projects/metrika/metrika-api/out/production/dbclients:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/jta-1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/lz4-1.1.2.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/jooq-3.4.1.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/httpcore-4.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/httpmime-4.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/snakeyaml-1.14.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/jooq-meta-3.4.1.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/httpclient-4.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/jooq-codegen-3.4.1.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/transactions-3.9.3.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/atomikos-util-3.9.3.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/fdb-sql-parser-1.6.1.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/transactions-api-3.9.3.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/transactions-jta-3.9.3.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/spring-tx-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/transactions-jdbc-3.9.3.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/mongo-java-driver-2.11.4.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/spring-jdbc-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/mysql-connector-java-5.1.31.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/spring-data-commons-1.5.2.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/dbclients/lib/default/spring-data-mongodb-1.3.1.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/out/test/managers-common:/home/orantius/dev/projects/metrika/metrika-api/out/production/managers-common:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/opencsv-2.3.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/commons-io-2.4.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/poi-3.10-FINAL.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/vrsnIdna-4.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/xmlbeans-2.6.0.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/servlet-api-3.0.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/stax2-api-3.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/freemarker-2.3.20.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/poi-ooxml-3.10-FINAL.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/validation-api-1.0.0.GA.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/commons-fileupload-1.3.1.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-io-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-jmx-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-xml-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-http-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-util-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jackson-dataformat-xml-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/poi-ooxml-schemas-3.10-FINAL.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-server-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-webapp-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-servlet-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/hibernate-validator-4.3.1.Final.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jackson-module-jsonSchema-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-security-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jetty-continuation-8.1.15.v20140411.jar:/home/orantius/dev/projects/metrika/metrika-api/frontend-common/lib/default/jackson-module-jaxb-annotations-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/out/test/mailer:/home/orantius/dev/projects/metrika/metrika-api/out/production/mailer:/home/orantius/dev/projects/metrika/metrika-api/mailer/lib/default/mail-1.4.5.jar:/home/orantius/dev/projects/metrika/metrika-api/mailer/lib/default/activation-1.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/mailer/lib/default/freemarker-2.3.20.jar:/home/orantius/dev/projects/metrika/metrika-api/mailer/lib/default/commons-email-1.3.2.jar:/home/orantius/dev/projects/metrika/metrika-api/out/production/bazinga-common:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/asm-all-5.0.3.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/jparsec-2.0.1.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/objenesis-2.1.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/stax2-api-3.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/zookeeper-3.4.5.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/protobuf-java-2.4.1.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/netty-all-4.0.15.Final.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/spring-tx-4.0.5.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/woodstox-core-asl-4.1.4.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/mongo-java-driver-2.11.4.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/spring-data-commons-1.5.2.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/spring-data-mongodb-1.3.1.RELEASE.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/inside-r20140530141418.57835fd6eeeb.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/commune-r20140530141418.57835fd6eeeb.jar:/home/orantius/dev/projects/metrika/metrika-api/bazinga-common/lib/default/commune-corba-r20140530141418.57835fd6eeeb.jar:/home/orantius/dev/projects/metrika/metrika-api/out/test/cluster-common:/home/orantius/dev/projects/metrika/metrika-api/out/production/cluster-common:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/test/curator-test-2.7.1.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/test/javassist-3.18.2-GA.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/stax2-api-3.1.1.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/zookeeper-3.4.6.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/curator-client-2.7.1.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/curator-recipes-2.7.1.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/curator-framework-2.7.1.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/woodstox-core-asl-4.1.4.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/jackson-dataformat-xml-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/cluster-common/lib/default/jackson-module-jaxb-annotations-2.4.0.jar:/home/orantius/dev/projects/metrika/metrika-api/out/production/mobmet-common:/home/orantius/dev/projects/metrika/metrika-api/out/test/markedphone-common:/home/orantius/dev/projects/metrika/metrika-api/out/production/markedphone-common:/home/orantius/dev/projects/metrika/metrika-api/markedphone-common/lib/default/xmlrpc-client-3.1.3.jar:/home/orantius/dev/projects/metrika/metrika-api/markedphone-common/lib/default/xmlrpc-common-3.1.3.jar:/home/orantius/dev/projects/metrika/metrika-api/markedphone-common/lib/default/xmlrpc-server-3.1.3.jar:/home/orantius/dev/projects/metrika/metrika-api/markedphone-common/lib/default/ws-commons-util-1.0.1.jar
java.class.version = 52.0
java.endorsed.dirs = /usr/lib/jvm/java-8-oracle/jre/lib/endorsed
java.ext.dirs = /usr/lib/jvm/java-8-oracle/jre/lib/ext:/usr/java/packages/lib/ext
java.home = /usr/lib/jvm/java-8-oracle/jre
java.io.tmpdir = /tmp
java.library.path = /home/orantius/dev/idea-IU-139.224.1/bin::/usr/java/packages/lib/amd64:/usr/lib64:/lib64:/lib:/usr/lib
java.runtime.name = Java(TM) SE Runtime Environment
java.runtime.version = 1.8.0_05-b13
java.specification.name = Java Platform API Specification
java.specification.vendor = Oracle Corporation
java.specification.version = 1.8
java.vendor = Oracle Corporation
java.vendor.url = http://java.oracle.com/
java.vendor.url.bug = http://bugreport.sun.com/bugreport/
java.version = 1.8.0_05
java.vm.info = mixed mode
java.vm.name = Java HotSpot(TM) 64-Bit Server VM
java.vm.specification.name = Java Virtual Machine Specification
java.vm.specification.vendor = Oracle Corporation
java.vm.specification.version = 1.8
java.vm.vendor = Oracle Corporation
java.vm.version = 25.5-b02
line.separator =

os.arch = amd64
os.name = Linux
os.version = 3.13.0-24-generic
path.separator = :
sun.arch.data.model = 64
sun.boot.class.path = /usr/lib/jvm/java-8-oracle/jre/lib/resources.jar:/usr/lib/jvm/java-8-oracle/jre/lib/rt.jar:/usr/lib/jvm/java-8-oracle/jre/lib/sunrsasign.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jsse.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jce.jar:/usr/lib/jvm/java-8-oracle/jre/lib/charsets.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jfr.jar:/usr/lib/jvm/java-8-oracle/jre/classes
sun.boot.library.path = /usr/lib/jvm/java-8-oracle/jre/lib/amd64
sun.cpu.endian = little
sun.cpu.isalist =
sun.desktop = gnome
sun.io.unicode.encoding = UnicodeLittle
sun.java.command = com.intellij.rt.execution.junit.JUnitStarter -ideVersion5 ru.yandex.metrika.schedulerd.util.MailSenderTest,testSendLetter
sun.java.launcher = SUN_STANDARD
sun.jnu.encoding = UTF-8    // ANSI_X3.4-1968
sun.management.compiler = HotSpot 64-Bit Tiered Compilers
sun.os.patch.level = unknown
user.country = US
user.dir = /home/orantius/dev/projects/metrika/metrika-api
user.home = /home/orantius
user.language = en
user.name = orantius
user.timezone = Europe/Moscow

*/
