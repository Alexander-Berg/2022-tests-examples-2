package ru.yandex.metrika.util.time;

import java.util.Arrays;
import java.util.Random;

import org.junit.Ignore;
import org.junit.Test;

/**
 * Created by orantius on 9/24/14.
 */
@Ignore
public class TripleTest {

    @Test
    public void realPowerTest() {
        /*
        HttpClient hc = new DefaultHttpClient();
        Map<String, Long> countByDC = Arrays.stream(new String[]{"mtolaprep", "mtolap_m", "mtcalclog"}).flatMap(g -> {
            HttpGet get = new HttpGet("http://c.yandex-team.ru/api/groups2hosts/" + g);
            String[] hosts = new String(Try.of(() -> ByteStreams.toByteArray(hc.execute(get).getEntity().getContent())).get()).split("\n");
            return Arrays.stream(hosts);
        }).map(h -> {
            HttpGet get = new HttpGet("http://c.yandex-team.ru/api/hosts/" + h);
            String xml = new String(Try.of(() -> ByteStreams.toByteArray(hc.execute(get).getEntity().getContent())).get());
            return xml.substring(xml.indexOf("<root_datacenter>") + "<root_datacenter>".length(), xml.indexOf("</root_datacenter>"));
        }).collect(Collectors.groupingBy(dc -> dc, Collectors.counting()));
        System.out.println("countByDC = " + countByDC); // collect = {ugr=4, fol=13, sas=4, iva=14, myt=9}
        */
        for(int ugr = 0; ugr <=4; ugr++) {
            for(int fol = 0; fol <= 13; fol++) {
                for(int sas = 0; sas <= 4; sas++) {
                    for(int iva = 0; iva <=14; iva++) {
                        for(int myt = 0; myt <=9 ; myt++) {
                            if(ugr+fol+sas+iva+myt == 21) {
                                int[] dcs = Arrays.stream(new int[]{ugr, fol, sas, iva, myt}).filter(h -> h > 0).toArray();
                                if(dcs.length >= 3 ) {
                                    int p = powerDCm1(dcs);
                                    if( p >= 16) {
                                        System.out.println("ugr = " + ugr + ", fol = " + fol + ", sas = " + sas+
                                                ", iva = " + iva+", myt = " + myt + ", p = " + p +" power = "+power(dcs));
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        /*
case 21:
ugr = 2, fol = 5, sas = 4, iva = 5, myt = 5, p = 16 power = 21
ugr = 3, fol = 4, sas = 4, iva = 5, myt = 5, p = 16 power = 21
ugr = 3, fol = 5, sas = 3, iva = 5, myt = 5, p = 16 power = 21
ugr = 3, fol = 5, sas = 4, iva = 4, myt = 5, p = 16 power = 21
ugr = 3, fol = 5, sas = 4, iva = 5, myt = 4, p = 16 power = 21
ugr = 4, fol = 3, sas = 4, iva = 5, myt = 5, p = 16 power = 21
ugr = 4, fol = 4, sas = 3, iva = 5, myt = 5, p = 16 power = 21
ugr = 4, fol = 4, sas = 4, iva = 4, myt = 5, p = 16 power = 21  <<<
ugr = 4, fol = 4, sas = 4, iva = 5, myt = 4, p = 16 power = 21  <<<
ugr = 4, fol = 5, sas = 2, iva = 5, myt = 5, p = 16 power = 21
ugr = 4, fol = 5, sas = 3, iva = 4, myt = 5, p = 16 power = 21
ugr = 4, fol = 5, sas = 3, iva = 5, myt = 4, p = 16 power = 21
ugr = 4, fol = 5, sas = 4, iva = 3, myt = 5, p = 16 power = 21
ugr = 4, fol = 5, sas = 4, iva = 4, myt = 4, p = 16 power = 21  <<<
ugr = 4, fol = 5, sas = 4, iva = 5, myt = 3, p = 16 power = 21

case 30:
ugr = 4, fol = 7, sas = 4, iva = 7, myt = 8, p = 22 power = 30
ugr = 4, fol = 7, sas = 4, iva = 8, myt = 7, p = 22 power = 30
ugr = 4, fol = 8, sas = 4, iva = 7, myt = 7, p = 22 power = 30*/
    }

// i<j<k dc[i]*dc[j]*dc[k]
    //   TODO: probability.
    @Test
    public void mainp() {
        int[] dcs = {10,10,10,1}; // x,x,x,y     30*x+y=1.       1000:    30/31*20/21*10/11
        int sum = Arrays.stream(dcs).sum();
        int[] cumsumDC = Arrays.copyOf(dcs, dcs.length);
        Arrays.parallelPrefix(cumsumDC,Integer::sum);

        double[] probs = new double[sum];
        Arrays.setAll(probs, k -> 1.0);
        for(int i = 0; i < dcs.length; i++) {
            double triples = 0;
            for(int j = 0; j < dcs.length; j++) {
                for(int k = j+1; k < dcs.length; k++) {
                    if(j!=i && k!=i) {
                        triples+=(dcs[j]*dcs[k]);
                    }
                }
            }
            for(int j = i==0?0:cumsumDC[i-1];j < cumsumDC[i]; j++) {
                probs[j] /= triples;
            }
        }
        double norm = Arrays.stream(probs).sum();
        for (int i = 0; i < probs.length; i++) {
            probs[i] /= norm;
        }

        double[] cumsumP = Arrays.copyOf(probs, probs.length);
        Arrays.parallelPrefix(cumsumP, Double::sum);
        Random r = new Random();

        int[] stats = new int[sum];
        for(int i = 0; i <100000; i++) {
            int dcmask = 0;
            while(Integer.bitCount(dcmask) < 3) {
                double p = r.nextDouble();
                //int index = (int)(p * sum);
                int dd = Arrays.binarySearch(cumsumP, p);
                int index = (-dd-1);
                int dcbit = 1<<getDC(cumsumDC, index);
                if((dcmask & dcbit) == 0) {
                    dcmask |= dcbit;
                    stats[index]++;
                }
            }
        }
        /*for(int i = 0; i < 100000; i++){
            double p = r.nextDouble();
            int index = Arrays.binarySearch(cumsumP, p);
            int dd = (-index-1);
            stats[dd]++;
        }*/
        System.out.println("stats = " + Arrays.toString(stats));
    }

    @Test
    public void powerTest() {
        for(int i = 10; i < 40; i++) {
            System.out.println("power(new int[]{"+i+","+i+",10,10,2}) = " + powerDCm1(new int[]{i, i, 10, 10, 2}));
        }
        for(int i = 10; i < 40; i++) {
            System.out.println("power(new int[]{"+i+",10,10,10,2}) = " + powerDCm1(new int[]{i, 10, 10, 10, 2}));
        }
    }


    public static int powerDCm1(int[] dcs) {
        int res = power(dcs);
        for(int i = 0; i < dcs.length; i++) {
            int[] ints = Arrays.copyOf(dcs, dcs.length);
            ints[i] = -1;
            int[] filtered = Arrays.stream(ints).filter(z -> z >= 0).toArray();
            res = Math.min(res, power(filtered));
        }
        return res;
    }

    public static int power(int[] dcs) {
        Arrays.sort(dcs);
        int sum = Arrays.stream(dcs).sum();
        int top = dcs[dcs.length-1];
        int top2 = dcs[dcs.length-2];
        int sumOther = sum-top-top2;
        top2 = Math.min(top2, sumOther);
        top = Math.min(top, (top2+sumOther)/2);
        int eff = top+top2+sumOther;
        return eff;
    }

    @Test
    public void tripleBias() {
        int[] dcs = {10,10,10,1};
        int sum = Arrays.stream(dcs).sum();
        int[] cumsum = Arrays.copyOf(dcs, dcs.length);
        Arrays.parallelPrefix(cumsum,Integer::sum);
        //   a ,  b   c
        // a      */b+c a+c /b+c a+b
        // b               /a+c a+b
        // c
        // total 2-tuples = ab + ac + bc.
        // a/p/(1-a/p)*b/(a+c)
        //   a/p-a *b/p-b + b/p-b * c/p-c+c/p-c * a/p-a = a/p-a *b/p-b * c/p-c (p-a/a + p-b/b + p-c/c) = Z
        // a*Pa+b*Pb+c*Pc = 1.
        //     20 30 40.
        Random r = new Random(42);

        int[] stats = new int[sum];
        for(int i = 0; i <100000; i++) {
            int dcmask = 0;
            while(Integer.bitCount(dcmask) < 3) {
                double p = r.nextDouble();
                int index = (int)(p * sum);
                int dcbit = 1<<getDC(cumsum, index);
                if((dcmask & dcbit) == 0) {
                    dcmask |= dcbit;
                    stats[index]++;
                }
            }
        }
        for (int i = 0; i < cumsum.length; i++) {
            System.out.println("stats = " + Arrays.stream(stats).skip(i>0?cumsum[i-1]:0).limit(dcs[i]).summaryStatistics());
        }
    }

    private static int getDC(int[] cumsum, int value) {
        int index = Arrays.binarySearch(cumsum, value);
        if(index >= 0) return index+1;
        return (-index-1);
    }
}
