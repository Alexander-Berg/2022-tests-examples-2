package ru.yandex.metrika.schedulerd.cron.task;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

import javax.annotation.PostConstruct;
import javax.mail.internet.InternetAddress;

import org.apache.commons.lang3.tuple.Pair;
import org.apache.commons.mail.Email;
import org.joda.time.DateTime;

import ru.yandex.metrika.dbclients.clickhouse.ClickhouseLogEntry;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.RowMappers;
import ru.yandex.metrika.mail.Message;
import ru.yandex.metrika.util.app.Env;
import ru.yandex.metrika.util.app.Settings;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.collections.Try;

/**
 * Created by hamilkar on 9/16/15.
 */
public class TestNotificationTask extends NotificationTask {

    private static final String TEST_EMAIL = "metrika-test-letters@yandex-team.ru";
    private TestUids testUids;

    @Override
    protected void process(int maxQueueSize, boolean isSms, Function<Message, Try<String>> sender) {
        log.info("is sms = {}", isSms);
        List<Message> messages = getMessageQueue().list(maxQueueSize, isSms);
        log.info("read {} messages from db", messages.size());
        responseLog(messages, NotificationTask.MessageLogEntry::new);

        List<Long> notSendingIds = messages.stream()
                .filter(message -> !testUids.contains(message.getUid()))
                .map(Message::getId).collect(Collectors.toList());
        messages = F.filter(messages, message -> testUids.contains(message.getUid()));

        log.info("sending {} letters on dev/test", messages.size());

        Map<Boolean, List<Pair<Message, Try<String>>>> status = messages.stream().map(m -> F.toPair(m, sender))
                .collect(Collectors.partitioningBy(p -> p.getRight().isSuccess()));
        List<Long> goodSentIds = status.get(Boolean.TRUE).stream().map(p -> p.getLeft().getId()).collect(Collectors.toList());
        // на ТС нужно отмечать как просроченные те письма, которые мы не хотим отправлять
        // иначе до нужных писем очередь не дойдет
        log.info("good ids size = {}", goodSentIds.size());
        getMessageQueue().markAsSent(goodSentIds);
        getMessageQueue().expire(notSendingIds);
        // there are some failed messages - find them and mark as failed
        status.get(Boolean.FALSE).forEach(p ->
                log.warn("error send message " + p.getLeft() + ' ', p.getRight().reasonOfFail()));
        List<Long> badSentIds = status.get(Boolean.FALSE).stream().map(p -> p.getLeft().getId()).collect(Collectors.toList());
        getMessageQueue().markAsFailed(badSentIds);
    }

    @Override
    protected Try<String> trySendLetter(Message message) {
        return Try.of(() -> {
            Email email = prepareLetter(message);
            InternetAddress internetAddress = new InternetAddress(TEST_EMAIL);
            internetAddress.validate();
            email.getToAddresses().add(internetAddress);
            return email.send();
        });
    }

    @Override
    public void execute() throws Exception {
        if (Settings.getEnv() != Env.testing) {
            log.info("will work only on test");
            return;
        }
        send();
    }

    public void setTestUids(TestUids testUids) {
        this.testUids = testUids;
    }


    public static class MessageLogEntry extends ClickhouseLogEntry {
        private final long id;
        private final long uid;
        private final int isSms;
        private final DateTime addTime;
        private final String message;

        public MessageLogEntry(Message msg) {
            id = msg.getId();
            uid = msg.getUid();
            isSms = msg.isSms() ? 1 : 0;
            addTime = msg.getAddTime();
            message = msg.getMessage();
        }

        public long getId() {
            return id;
        }

        public long getUid() {
            return uid;
        }

        public int isSms() {
            return isSms;
        }

        public DateTime getAddTime() {
            return addTime;
        }

        public String getMessage() {
            return message;
        }
    }

    public static class TestUids {
        private Set<Long> uids = new HashSet<>();
        private MySqlJdbcTemplate convMain;

        public boolean contains(long uid) {
            return uids.contains(uid);
        }

        @PostConstruct
        public void reload() {
            uids = new HashSet<>(convMain.query("SELECT uid FROM test_uids", RowMappers.LONG));
        }

        public void setConvMain(MySqlJdbcTemplate convMain) {
            this.convMain = convMain;
        }
    }
}
