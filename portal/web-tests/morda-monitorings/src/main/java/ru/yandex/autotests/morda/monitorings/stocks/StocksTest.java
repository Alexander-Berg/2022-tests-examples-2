package ru.yandex.autotests.morda.monitorings.stocks;

import org.junit.Test;
import ru.yandex.autotests.morda.beans.exports.stocks.StocksEntry;
import ru.yandex.autotests.morda.beans.exports.stocks.StocksExport;
import ru.yandex.autotests.morda.beans.stocks.StocksItem;
import ru.yandex.autotests.morda.beans.stocks.StocksResponse;
import ru.yandex.autotests.morda.utils.client.MordaClientBuilder;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.client.Client;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/11/15
 */
public class StocksTest {


    public static boolean isRegionAccepted(List<Integer> parents, String exportRegion) {
        List<Integer> splitted = asList(exportRegion.split(",")).stream()
                .map(e -> Integer.parseInt(e.trim()))
                .sorted(Integer::compare)
                .filter(e -> e > 0)
                .collect(Collectors.toList());

        parents.retainAll(splitted);

        return parents.size() > 0;
    }

    public static StocksItem getItem(List<StocksItem> items, String id, String geoId) {
        try {
            Integer.parseInt(geoId);
        } catch (Exception e) {
            return null;
        }
        List<Integer> parents = new GeobaseRegion(Integer.parseInt(geoId)).getParentsIds();
        for (Integer region : parents) {
            Optional<StocksItem> item = items.stream()
                    .filter(s -> {
                        return (s.getId() + "").equals(id) && s.getGeo() == region;
                    })
                    .sorted((s1, s2) -> s2.getDt().compareTo(s1.getDt()))
                    .findFirst();

            if (item.isPresent()) {
                return item.get();
            }
        }
        return null;
    }

    @Test
    public void t() {
        Client client = MordaClientBuilder.mordaClient()
                .withLogging(true)
                .failOnUnknownProperties(false)
                .build();

        StocksResponse stocksData = client.target("http://stocks.yandex.net/morda-v2.json")
                .request()
                .buildGet()
                .invoke()
                .readEntity(StocksResponse.class);

        int region = 2;
        List<Integer> parents = new GeobaseRegion(region).getParentsIds();

        List<StocksEntry> stocksExport = new StocksExport().populate().getData()
                .stream()
                .filter(e -> isRegionAccepted(parents, e.getGeo()))
                .collect(Collectors.toList());

//        stocksExport.stream().forEach(e -> {
//            System.out.println(e.getId() + " " + e.getGeo() + " " + e.getText());
//        });

        stocksExport.forEach(e -> {
            System.out.println(e.getId() + "\t" + e.getText() + "\t" + e.getType() + "\t" + e.getGeo());

            StocksItem item = getItem(stocksData.getStocks(), e.getId(), region + "");
            if (item == null) {
                System.out.println(item);
            } else {
                System.out.println(item.getId() + "\t" + item.getDt() + "\t" + item.getGeo());
            }
            System.out.println();
//            System.out.println();
//            stocksData.getStocks().stream()
//                    .filter(s -> (s.getId() + "").equals(e.getId()))
//                    .sorted((s1, s2) -> s2.getDt().compareTo(s1.getDt()))
//                    .forEach(s -> {
//                        System.out.println(s.getId() + " " + s.getDt() + " " + s.getGeo());
//                    });

        });


    }
}
