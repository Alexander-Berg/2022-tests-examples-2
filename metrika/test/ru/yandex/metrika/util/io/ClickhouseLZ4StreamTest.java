package ru.yandex.metrika.util.io;

import java.io.InputStream;
import java.util.Scanner;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClientBuilder;
import org.junit.Ignore;

@Ignore
public class ClickhouseLZ4StreamTest {
    public static void main(String[] args) throws Exception {
        HttpClient client = HttpClientBuilder.create().build();
        HttpGet httpGet = new HttpGet("http://localhost:38123/?compress=1&query=select%20(StartURL)%20as%20p,%20count()%20from%20merge.visits%20where%20CounterID%20=%20101024%20and%20StartDate%20%3E%20toDate('2013-06-01')%20and%20StartDate%20%3C%20toDate('2013-06-03')%20GROUP%20BY%20p%20WITH%20TOTALS%20FORMAT%20JSONCompact");
        HttpResponse execute = client.execute(httpGet);
        InputStream content = execute.getEntity().getContent();

        /*int r = content.read();
        while(r >= 0) {
            System.out.println(r);
            r = content.read();
        }*/

        ClickhouseLZ4Stream lz4Stream = new ClickhouseLZ4Stream(content);
        System.out.println(new Scanner(lz4Stream).useDelimiter("\\A").next());
    }

}
