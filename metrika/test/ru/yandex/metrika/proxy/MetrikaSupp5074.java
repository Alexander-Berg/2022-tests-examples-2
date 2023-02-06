package ru.yandex.metrika.proxy;

import com.google.common.io.ByteStreams;
import org.apache.http.Header;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.message.BasicHeader;
import org.apache.logging.log4j.Level;

import ru.yandex.metrika.util.http.SSLUtils;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * Created by orantius on 5/26/15.
 */
public class MetrikaSupp5074 {
    // Емкость пула, сколько всего коннектов
    private static int maxTotalConnections = 500;
    // Макс кол-во коннектов на один хост
    private static int maxConnectionsPerRoute = 10;
    // Таймаут подключения к сайту, в секундах
    private static int connectTimeout = 30;
    // Таймаут ввода-вывода в сокет, в секундах
    private static int socketTimeout = 60;

    public static void main(String[] args) {
        Log4jSetup.basicSetup(Level.DEBUG);
        HttpGet httpget = null;
        try {
            httpget = new HttpGet("https://www.strategshop.ru/");
            httpget.setHeaders(new Header[]{
                    new BasicHeader("Host","strategshop.ru"),
                    new BasicHeader("User-Agent","Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"),
                    new BasicHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                    new BasicHeader("Accept-Language","en-US,en;q=0.5"),
                    new BasicHeader("Accept-Encoding","gzip, deflate"),
                    new BasicHeader("Cookie","ga=GA1.2.2117919654.1432571488; _gat=1; _ym_visorc_27444132=w"),
                    new BasicHeader("Connection","keep-alive"),
                    new BasicHeader("Pragma","no-cache"),
                    new BasicHeader("Cache-Control","no-cache")
            });
            //copyRequestHeaders(httpReq, httpget);
            HttpClient sslv3httpClient = SSLUtils.makeTrustfulProxyClient(socketTimeout, connectTimeout, maxTotalConnections, maxConnectionsPerRoute);
            HttpResponse hostResponse = sslv3httpClient.execute(httpget);
            StatusLine status = hostResponse.getStatusLine();
            int statusCode = status.getStatusCode();
            //376296    1153.286652000    95.108.172.157    89.169.109.194    SSL    278    Client Hello
            //copyResponseHeaders(hostResponse, httpResp, proxyUri);
            HttpEntity entity = hostResponse.getEntity();

            String s = new String(ByteStreams.toByteArray(entity.getContent()));
            System.out.println(hostResponse.getStatusLine()+"\n" + s);
            //if (entity != null)
                //copyResponseBody(entity, httpResp);
        } catch (Exception e) {
            System.out.println("e = " + e);
            e.printStackTrace();
        } finally {

            if (httpget != null)
                httpget.releaseConnection();
        }
        System.out.println("***Request handled strategshop.ru");

    }
}
