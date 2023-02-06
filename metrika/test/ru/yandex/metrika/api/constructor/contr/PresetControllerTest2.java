package ru.yandex.metrika.api.constructor.contr;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;

import com.codahale.metrics.MetricRegistry;
import com.codahale.metrics.Snapshot;
import com.codahale.metrics.Timer;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.junit.Ignore;
import org.junit.Test;

/**
 * @author orantius
 * @version $Id$
 * @since 12/4/13
 */
@Ignore
public class PresetControllerTest2 {

    @Test
    public void testPreset() {
        MetricRegistry mr = new MetricRegistry();
        Timer preset = mr.timer("preset");
        for (int i = 0; i < 10000; i++) {
            final Timer.Context context = preset.time();
            try {
                String s = sendRequest("http://localhost:8082/secure/api/preset.json?name=traffic&with_tree=1&uid_real=22892801&uid=22892801&lang=ru");
                //System.out.println(s);
            } finally {
                context.stop();
            }
        }

        System.out.println("preset = " + toString(preset.getSnapshot()));
        /*
        in test                 internal
        min=4.355509,           3
        median=15.672516        13
        mean=17.25371354474708  15.46
        75%=19.03607875  ,      16
        95%=25.58796040         22
        98%=32.48680374         31.4
        99%=38.51221552         37.8
        max=487.489681,         485

no spring-securitity
        min=4246274,median=13858529,mean=13622450,75%=15144283,95%=20989507,98%=23939020,99%=31673895,max=147866839
        * */
    }

    public String toString(Snapshot snapshot) {
        return new ToStringBuilder(this).
             append("min", (long)snapshot.getMin()).
             append("median", (long)snapshot.getMedian()).
             append("mean", (long)snapshot.getMean()).
             append("75%", (long)snapshot.get75thPercentile()).
             append("95%", (long)snapshot.get95thPercentile()).
             append("98%", (long)snapshot.get98thPercentile()).
             append("99%", (long) snapshot.get99thPercentile()).
             append("max", (long) snapshot.getMax()).
          toString();
    }

    private static String sendRequest(String url) {
        StringBuilder ret = new StringBuilder();
        try {
            URL u = new URL(url);
            URLConnection uc = u.openConnection();
            BufferedReader in = new BufferedReader(new InputStreamReader(uc.getInputStream()));
            String line;
            while ((line = in.readLine()) != null) {
                ret.append(line);
            }
            in.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return ret.toString();
    }

}
