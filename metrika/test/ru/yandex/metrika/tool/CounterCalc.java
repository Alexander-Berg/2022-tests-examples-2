package ru.yandex.metrika.tool;


import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.regex.Pattern;

/**
 * @author asuilin
 * @version $Id$
 * @since 16.12.10
 */
public class CounterCalc {
    private static final Pattern PATTERN = Pattern.compile("\\t");

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("/home/asuilin/all_counters.csv")));
        int count = 0;
        int sum = 0;
        int selectedSum = 0;
        int totalRbac = 0;
        while (br.ready()) {
            String s = br.readLine();
            String[] parts = PATTERN.split(s);
            count++;
            if (count < 10) {
                continue;
            }
            int n = Math.round(Float.parseFloat(parts[1]));
            sum += n;
            int recorded = n <= 1000 ? n : 1000;
            selectedSum += recorded;
            double rbacQ = Math.min(recorded, 24);
            totalRbac += rbacQ;
        }
        br.close();
        int hitKeySize = 4 + 8 + 8 + 4;
        System.out.println(String.format("%d counters, %d visits, %d selected visits, %d visit per counter, %f percent selected", count, sum, selectedSum, selectedSum / count, selectedSum * 100f / sum));
        int bloomVisitSize = selectedSum * 10 / 8/1024/1024;
        double bloomSelectedHitsSize = 2.5 * selectedSum * 10 / 8 / 1024 /1024 ;
        double bloomUnselectedHitsSize = 2.5 * sum * 10 / 8 /1024/1024 - bloomSelectedHitsSize;
        double  keySelectedHitsSize = 2.5 * selectedSum * hitKeySize / 1024 /1024 ;
        double keyUnselectedHitsSize = 2.5 * sum * hitKeySize /1024/1024 - keySelectedHitsSize;


        //int bloomHitSize = selectedSum * 10 *  / 81024;
        System.out.println(String.format("Bloom: visits %d, selected hits %f, unselected hits %f", bloomVisitSize, bloomSelectedHitsSize, bloomUnselectedHitsSize));
        System.out.println(String.format("Hit external keys: selected %f, unselected %f", keySelectedHitsSize, keyUnselectedHitsSize));
        System.out.println(String.format("Rbac queries: %d, %f per second", totalRbac, totalRbac / 24f / 3600f));
    }
}
