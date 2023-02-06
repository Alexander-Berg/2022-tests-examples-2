package ru.yandex.metrika.api.management;

import java.util.Comparator;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

import org.apache.logging.log4j.Level;

import ru.yandex.metrika.api.management.client.model.DatabaseFilter;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * Created by orantius on 8/26/15.
 */
public class FilterSerialFix {
    public static void main(String[] args) {
        Log4jSetup.basicSetup(Level.DEBUG);
        MySqlJdbcTemplate template = AllDatabases.getTemplate("localhost", 3312, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
        List<DatabaseFilter> fs = template.query("select * from Filters where Status = 'Active' ", (rs, i) -> {
            int id = rs.getInt("ID");
            int counterId = rs.getInt("CounterID");
            String attr = rs.getString("AttributeName");
            String type = rs.getString("Type");
            String value = rs.getString("Value");
            String status = rs.getString("Status");
            String data = rs.getString("Data");
            boolean withSubdomains = rs.getBoolean("WithSubdomains");
            int serial = rs.getInt("Serial");

            DatabaseFilter dbFilter = new DatabaseFilter(id, counterId, attr, type, value, data, status, withSubdomains, serial);
            return dbFilter;
        });
        System.out.println("fs = " + fs.size());
        Map<Integer, List<DatabaseFilter>> byCounter = fs.stream().sorted(Comparator.comparing(DatabaseFilter::getId)).collect(Collectors.groupingBy(DatabaseFilter::getCounterId));
        TreeSet<Integer> serials = new TreeSet<>();
        for (Map.Entry<Integer, List<DatabaseFilter>> ee : byCounter.entrySet()) {
            List<DatabaseFilter> dfs = ee.getValue();
            serials.clear();
            for (DatabaseFilter df : dfs) {
                serials.add(df.getSerial());
            }
            if(dfs.size() == serials.size())
                continue; // если совпадений нет - ок.

            List<DatabaseFilter> zeroS = dfs.stream().filter(f -> f.getSerial() == 0).collect(Collectors.toList());
            Integer maxSerial = serials.last();
            AtomicInteger next = new AtomicInteger(maxSerial+1);
            zeroS.stream().filter(f -> f.getSerial() == 0).forEach(f -> f.setSerial(next.getAndIncrement()));
            int sum = zeroS.stream().map(f -> "update Filters set Serial = " + f.getSerial() + " where ID = " + f.getId())
                    .mapToInt(template::update).sum();
            System.out.println(new Date()+": zeroS = " + zeroS.size()+" updated "+sum+" id="+ee.getKey());
        }
    }


}
