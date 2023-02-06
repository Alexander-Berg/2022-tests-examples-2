package ru.yandex.autotests.mordalinks.utils;

import ru.yandex.autotests.mordalinks.beans.MordaLinksCount;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.util.JAXBSource;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import java.io.ByteArrayOutputStream;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 30.05.14
 */
public class PageUtils {

    public static final String MESSAGE_XSL = "xsl/message.xsl";

    public static byte[] createMessage(MordaLinksCount list) throws Exception {
        MessagePage page = new MessagePage()
                .withCount(list.getCount());

        return transform(MessagePage.class, MESSAGE_XSL, page);
    }

    private static  <T> byte[] transform(Class<T> clazz, String xsl, T page) throws Exception {
        TransformerFactory tf = TransformerFactory.newInstance();
        StreamSource xslt = new StreamSource(PageUtils.class.getClassLoader().getResourceAsStream(xsl));
        Transformer transformer = tf.newTransformer(xslt);

        JAXBContext jc = JAXBContext.newInstance(clazz);
        JAXBSource source = new JAXBSource(jc, page);

        ByteArrayOutputStream bos = new ByteArrayOutputStream();

        StreamResult result = new StreamResult(bos);

        transformer.transform(source, result);

        return bos.toByteArray();
    }

}
