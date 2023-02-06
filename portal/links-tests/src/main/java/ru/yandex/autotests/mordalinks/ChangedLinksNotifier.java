package ru.yandex.autotests.mordalinks;

import org.apache.commons.io.IOUtils;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordalinks.beans.MordaLinksCount;
import ru.yandex.autotests.utils.morda.mail.MailUtils;

import java.io.IOException;

import static ru.yandex.autotests.mordalinks.utils.MordaLinkUtils.getChangedLinksCount;
import static ru.yandex.autotests.mordalinks.utils.PageUtils.createMessage;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.09.14
 */
public class ChangedLinksNotifier {
    private static final Logger LOG = Logger.getLogger(ChangedLinksNotifier.class);

    public static void main(String[] args) throws Exception {
        MordaLinksCount count = getChangedLinksCount();
        if (count.getCount() > 0) {
            sendMessage(createMessage(count));
        }
    }

    private static void sendMessage(byte[] message) throws IOException {
        MailUtils.mail()
                .setFrom("eoff@yandex-team.ru")
                .setTo("morda-reports@yandex-team.ru")
                .setSubject("Morda Links Check")
                .setText(IOUtils.toString(message, "UTF-8"))
                .send();
    }

}
