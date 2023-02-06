package ru.yandex.metrika.filterd.process;

import com.google.common.primitives.Bytes;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.Base64;
import ru.yandex.metrika.visord.chunks.EventMessageType;

import static org.junit.Assert.assertArrayEquals;

/**
 * @author orantius
 * @version $Id$
 * @since 6/3/11
 */
public class EventLogTest {
    @Before
    public void setUp() throws Exception {

    }

    @Test
    public void testEncodingChange() throws Exception {
        //"Артемий Лебедев"
        byte[] utf8 = {-48, -112, -47, -128, -47, -126, -48, -75, -48, -68, -48, -72, -48, -71, 32, -48,
                -101, -48, -75, -48, -79, -48, -75, -48, -76, -48, -75, -48, -78};
        byte[] windows1251 = {-64, -16, -14, -27, -20, -24, -23, 32, -53, -27, -31, -27, -28, -27, -30};
        char[] base64 = Base64.CLASSIC.encode(utf8);
        EventLogCommonMetadata metadata = new EventLogCommonMetadata();
        metadata.messageType = EventMessageType.EVENT;
        metadata.contentType = EventContentType.MULTIPART_DECODED;
        metadata.encoding = "text/html; charset=windows-1251";
        byte[] base64bytes = new byte[base64.length];
        for (int i = 0; i < base64.length; i++) {
            base64bytes[i] = (byte)base64[i];
        }
        byte[] start = "-----------------------------7dc2ac151390b7a\n\n\n".getBytes();
        byte[] end = "\n\n\n\n-----------------------------7dc2ac151390b7a".getBytes();
        byte[] toDecode = Bytes.concat(start, base64bytes, end);
        System.out.println(new String(toDecode, "utf-8"));
        byte[] decoded = windows1251; // MULTIPART IS NO MORE
        // EventLog.buildData(toDecode, metadata);
        System.out.println(new String(decoded, "windows-1251"));
        assertArrayEquals(windows1251, decoded);

    }

    @Test
    public void testTrim() throws Exception {
        String pageToTrim = "-----------------------------7dc2ac151390b7a\n" +
                "Content-Disposition: form-data; name=\"wv-data\"\n" +
                '\n' +
                "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n" +
                "<html><head><title>RU BC345 - Букет \"В плену любви\"</title><meta content=\"text/html; charset=windows-1251\" http-equiv=Content-Type><link rel=\"StyleSheet\" href=\"/css/sendflowers2/style.css\" type=\"text/css\" ></head><body>\n" +
                "<SCRIPT type=\"text/javascript\">\n" +
                '\n' +
                "var viewerType = \"0\";\n" +
                "var fetchedImages = {};\n" +
                "var imgThumbArr = [];\n" +
                "var numberToPreload = 8;\n" +
                "var preloadCount = 0;\n" +
                "var arrayindex = 0;\n" +
                "function fetchImage(id, image) \n" +
                "{\n" +
                "   fetchedImages[id] = {};\n" +
                "   fetchedImages[id].image = image;\n" +
                "   imgThumbArr[arrayindex] = id;\n" +
                "   arrayindex++;\n" +
                "   if(preloadCount < numberToPreload) \n" +
                "   {\n" +
                "     var imagePreloader = new Image();\n" +
                "     imagePreloader.src = image;\n" +
                "     preloadCount++;\n" +
                "   }\n" +
                "}\n" +
                "var allPreloaded = 0;\n" +
                '\n' +
                "function showImageViewer( id )\n" +
                "{\n" +
                "    document.getElementById('imageViewerDiv').style.width = 500;\n" +
                "    //document.getElementById('imageViewerDiv').style.height = 500;\n" +
                "    document.getElementById('imageViewerDiv').style.visibility = \"visible\";\n" +
                "    //document.getElementById('imageViewerDiv').style.vertical-align = \"middle\";\n" +
                '\n' +
                "    document.getElementById('imageViewerDiv').innerHTML = '<img src=\"\" id=\"pImage\" />';\n" +
                "    document.getElementById('pImage').src = fetchedImages[id].image;\n" +
                '\n' +
                "    for ( elementID in fetchedImages )\n" +
                "    {\n" +
                "      if ( !allPreloaded )\n" +
                "      {\n" +
                "        var imagePreloader = new Image();\n" +
                "        imagePreloader.src = fetchedImages[elementID].image;\n" +
                "      }\n" +
                "    }\n" +
                "    allPreloaded = 1;\n" +
                "}\n" +
                "</script>\n" +
                "<script type=\"text/javascript\">\n" +
                "<!--\n" +
                "var message=\"\";\n" +
                "///////////////////////////////////\n" +
                "function clickIE() {if (document.all) {(message);return false;}}\n" +
                "function clickNS(e) {if \n" +
                "(document.layers||(document.getElementById&&!document.all)) {\n" +
                "if (e.which==2||e.which==3) {(message);return false;}}}\n" +
                "if (document.layers) \n" +
                "{document.captureEvents(Event.MOUSEDOWN);document.onmousedown=clickNS;}\n" +
                "else{document.onmouseup=clickNS;document.oncontextmenu=clickIE;}\n" +
                "document.oncontextmenu=new Function(\"return false\")\n" +
                "// --> \n" +
                "</script>\n" +
                "<script type=\"text/javascript\">\n" +
                "window.focus();\n" +
                "</script>\n" +
                "<table cellpadding=\"1\" cellspacing=\"5\" width=\"100%\" align=\"center\"><tr><td><div style=\"float: right\"><a href=\"http://www.sendflowers.ru\" target=new><img src=\"/images/sendflowers2/sendflowers-v2.gif\" border=\"0\" height=\"26\" width=\"186\" alt=\"\" /></a></div><span class=TID>RU BC345</span><br/><span class=\"priceTextGreen\">Букет \"В плену любви\"</span></td></tr></table><table cellpadding=\"1\" cellspacing=\"5\" width=\"100%\" style=\"border:1px dashed #ddd;\"  align=\"center\"><tr><td colspan=\"2\"><span style=\"font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;\" class=\"f11 fr likea\"><a href=\"javascript: close();\">закрыть окно</a></span><span class=\"smalltext\">кликните на картинку для её просмотра</span></td></tr><tr><td colspan=\"2\"><table border=\"0\"><tr><td width=\"60\"><div onclick=\"showImageViewer('alt_image_1'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_f3da5741acee27199880f7cd9528a713.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=1&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td><td width=\"60\"><div onclick=\"showImageViewer('alt_image_2'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_3d8cbfc5630e112e4b8db334746b5072.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=2&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td><td width=\"60\"><div onclick=\"showImageViewer('alt_image_3'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_8550a0f49826f94dad29b86cddbd28d1.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=3&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td><td width=\"60\"><div onclick=\"showImageViewer('alt_image_4'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_b579939698ef2afd17cb00754c68a8d6.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=4&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td></tr></table></td></tr><tr style=\"\"><td style=\"border-top:1px dashed #ddd;\" colspan=\"2\" align=\"center\" valign=\"middle\"><noscript><div id=\"imageViewerDiv\"><img border=\"0\" src=\"/images/flowers/sendflowers2/small/500x570x0x0x95x1_f3da5741acee27199880f7cd9528a713.jpg\" id=\"pImage\" alt=\"\" /></div></noscript><script type=\"text/javascript\">var imageViewerTagDiv = '<div id=\"imageViewerDiv\"><img border=\"0\" src=\"/images/flowers/sendflowers2/small/500x570x0x0x95x1_f3da5741acee27199880f7cd9528a713.jpg\" id=\"pImage\" alt=\"\" \\/><\\/div>';document.write(imageViewerTagDiv);</script></td></tr></table> <script type=\"text/javascript\">\n" +
                "fetchImage('alt_image_1', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_f3da5741acee27199880f7cd9528a713.jpg');\n" +
                "fetchImage('alt_image_2', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_3d8cbfc5630e112e4b8db334746b5072.jpg');\n" +
                "fetchImage('alt_image_3', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_8550a0f49826f94dad29b86cddbd28d1.jpg');\n" +
                "fetchImage('alt_image_4', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_b579939698ef2afd17cb00754c68a8d6.jpg');\n" +
                "</script></body>\n" +
                "<!-- Yandex.Metrika counter -->\n" +
                "<div style=\"display:none;\"><script type=\"text/javascript\">\n" +
                "(function(w, c) {\n" +
                "(w[c] = w[c] || []).push(function() {\n" +
                "try {\n" +
                "w.yaCounter101024 = new Ya.Metrika({id:101024, clickmap:true, trackLinks:true});\n" +
                "}\n" +
                "catch(e) { }\n" +
                "});\n" +
                "})(window, 'yandex_metrika_callbacks');\n" +
                "</script></div>\n" +
                "<script src=\"//mc.yandex.ru/metrika/watch_visor.js\"\n" +
                "type=\"text/javascript\" defer=\"defer\"></script>\n" +
                "<noscript><div><img src=\"//mc.yandex.ru/watch/101024\"\n" +
                "style=\"position:absolute; left:-9999px;\" alt=\"\" /></div></noscript>\n" +
                "<!-- /Yandex.Metrika counter -->\n" +
                '\n' +
                "</html>\n" +
                "-----------------------------7dc2ac151390b7a--\n";
        String expected = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n" +
                "<html><head><title>RU BC345 - Букет \"В плену любви\"</title><meta content=\"text/html; charset=windows-1251\" http-equiv=Content-Type><link rel=\"StyleSheet\" href=\"/css/sendflowers2/style.css\" type=\"text/css\" ></head><body>\n" +
                "<SCRIPT type=\"text/javascript\">\n" +
                '\n' +
                "var viewerType = \"0\";\n" +
                "var fetchedImages = {};\n" +
                "var imgThumbArr = [];\n" +
                "var numberToPreload = 8;\n" +
                "var preloadCount = 0;\n" +
                "var arrayindex = 0;\n" +
                "function fetchImage(id, image) \n" +
                "{\n" +
                "   fetchedImages[id] = {};\n" +
                "   fetchedImages[id].image = image;\n" +
                "   imgThumbArr[arrayindex] = id;\n" +
                "   arrayindex++;\n" +
                "   if(preloadCount < numberToPreload) \n" +
                "   {\n" +
                "     var imagePreloader = new Image();\n" +
                "     imagePreloader.src = image;\n" +
                "     preloadCount++;\n" +
                "   }\n" +
                "}\n" +
                "var allPreloaded = 0;\n" +
                '\n' +
                "function showImageViewer( id )\n" +
                "{\n" +
                "    document.getElementById('imageViewerDiv').style.width = 500;\n" +
                "    //document.getElementById('imageViewerDiv').style.height = 500;\n" +
                "    document.getElementById('imageViewerDiv').style.visibility = \"visible\";\n" +
                "    //document.getElementById('imageViewerDiv').style.vertical-align = \"middle\";\n" +
                '\n' +
                "    document.getElementById('imageViewerDiv').innerHTML = '<img src=\"\" id=\"pImage\" />';\n" +
                "    document.getElementById('pImage').src = fetchedImages[id].image;\n" +
                '\n' +
                "    for ( elementID in fetchedImages )\n" +
                "    {\n" +
                "      if ( !allPreloaded )\n" +
                "      {\n" +
                "        var imagePreloader = new Image();\n" +
                "        imagePreloader.src = fetchedImages[elementID].image;\n" +
                "      }\n" +
                "    }\n" +
                "    allPreloaded = 1;\n" +
                "}\n" +
                "</script>\n" +
                "<script type=\"text/javascript\">\n" +
                "<!--\n" +
                "var message=\"\";\n" +
                "///////////////////////////////////\n" +
                "function clickIE() {if (document.all) {(message);return false;}}\n" +
                "function clickNS(e) {if \n" +
                "(document.layers||(document.getElementById&&!document.all)) {\n" +
                "if (e.which==2||e.which==3) {(message);return false;}}}\n" +
                "if (document.layers) \n" +
                "{document.captureEvents(Event.MOUSEDOWN);document.onmousedown=clickNS;}\n" +
                "else{document.onmouseup=clickNS;document.oncontextmenu=clickIE;}\n" +
                "document.oncontextmenu=new Function(\"return false\")\n" +
                "// --> \n" +
                "</script>\n" +
                "<script type=\"text/javascript\">\n" +
                "window.focus();\n" +
                "</script>\n" +
                "<table cellpadding=\"1\" cellspacing=\"5\" width=\"100%\" align=\"center\"><tr><td><div style=\"float: right\"><a href=\"http://www.sendflowers.ru\" target=new><img src=\"/images/sendflowers2/sendflowers-v2.gif\" border=\"0\" height=\"26\" width=\"186\" alt=\"\" /></a></div><span class=TID>RU BC345</span><br/><span class=\"priceTextGreen\">Букет \"В плену любви\"</span></td></tr></table><table cellpadding=\"1\" cellspacing=\"5\" width=\"100%\" style=\"border:1px dashed #ddd;\"  align=\"center\"><tr><td colspan=\"2\"><span style=\"font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;\" class=\"f11 fr likea\"><a href=\"javascript: close();\">закрыть окно</a></span><span class=\"smalltext\">кликните на картинку для её просмотра</span></td></tr><tr><td colspan=\"2\"><table border=\"0\"><tr><td width=\"60\"><div onclick=\"showImageViewer('alt_image_1'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_f3da5741acee27199880f7cd9528a713.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=1&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td><td width=\"60\"><div onclick=\"showImageViewer('alt_image_2'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_3d8cbfc5630e112e4b8db334746b5072.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=2&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td><td width=\"60\"><div onclick=\"showImageViewer('alt_image_3'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_8550a0f49826f94dad29b86cddbd28d1.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=3&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td><td width=\"60\"><div onclick=\"showImageViewer('alt_image_4'); return false\"  style=\"cursor:pointer;width:43px;height:50px;border: 1px solid #E5E5E5;background:#fff  url('/images/flowers/sendflowers2/small/43x50x2xWx95_b579939698ef2afd17cb00754c68a8d6.jpg') center; background-repeat: no-repeat;\"><a href=\"/inc/viewphotobig.phtml?CID=504&AID=0&kp=4&lid=1\"><img src=\"/images/pixel.gif\" width=\"43\" height=\"50\" border=\"0\" alt=\"\" /></a></div></td></tr></table></td></tr><tr style=\"\"><td style=\"border-top:1px dashed #ddd;\" colspan=\"2\" align=\"center\" valign=\"middle\"><noscript><div id=\"imageViewerDiv\"><img border=\"0\" src=\"/images/flowers/sendflowers2/small/500x570x0x0x95x1_f3da5741acee27199880f7cd9528a713.jpg\" id=\"pImage\" alt=\"\" /></div></noscript><script type=\"text/javascript\">var imageViewerTagDiv = '<div id=\"imageViewerDiv\"><img border=\"0\" src=\"/images/flowers/sendflowers2/small/500x570x0x0x95x1_f3da5741acee27199880f7cd9528a713.jpg\" id=\"pImage\" alt=\"\" \\/><\\/div>';document.write(imageViewerTagDiv);</script></td></tr></table> <script type=\"text/javascript\">\n" +
                "fetchImage('alt_image_1', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_f3da5741acee27199880f7cd9528a713.jpg');\n" +
                "fetchImage('alt_image_2', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_3d8cbfc5630e112e4b8db334746b5072.jpg');\n" +
                "fetchImage('alt_image_3', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_8550a0f49826f94dad29b86cddbd28d1.jpg');\n" +
                "fetchImage('alt_image_4', '/images/flowers/sendflowers2/small/500x570x0x0x95x1_b579939698ef2afd17cb00754c68a8d6.jpg');\n" +
                "</script></body>\n" +
                "<!-- Yandex.Metrika counter -->\n" +
                "<div style=\"display:none;\"><script type=\"text/javascript\">\n" +
                "(function(w, c) {\n" +
                "(w[c] = w[c] || []).push(function() {\n" +
                "try {\n" +
                "w.yaCounter101024 = new Ya.Metrika({id:101024, clickmap:true, trackLinks:true});\n" +
                "}\n" +
                "catch(e) { }\n" +
                "});\n" +
                "})(window, 'yandex_metrika_callbacks');\n" +
                "</script></div>\n" +
                "<script src=\"//mc.yandex.ru/metrika/watch_visor.js\"\n" +
                "type=\"text/javascript\" defer=\"defer\"></script>\n" +
                "<noscript><div><img src=\"//mc.yandex.ru/watch/101024\"\n" +
                "style=\"position:absolute; left:-9999px;\" alt=\"\" /></div></noscript>\n" +
                "<!-- /Yandex.Metrika counter -->\n" +
                '\n' +
                "</html>";
    }
}
// WebVisorLog20110603151401030
