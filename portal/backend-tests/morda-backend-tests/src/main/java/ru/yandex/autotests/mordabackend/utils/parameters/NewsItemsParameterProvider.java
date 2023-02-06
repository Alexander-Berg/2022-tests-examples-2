package ru.yandex.autotests.mordabackend.utils.parameters;

import ch.lambdaj.Lambda;
import ch.lambdaj.function.convert.Converter;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTabItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class NewsItemsParameterProvider implements ParameterProvider {
    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                    Region region, Language language, UserAgent userAgent) {
        List<Object[]> news = new ServicesV122ParameterProvider("news")
                .getParams(mordaClient, client, cleanvars, region, language, userAgent);
        if (news.size() != 1 || news.get(0).length != 1) {
            throw new RuntimeException("failed to create testdata");
        }
        final Object export = news.get(0)[0];

        List<Object[]> res = new ArrayList<>();

        for (List<Object[]> o :
                convert(cleanvars.getTopnews().getTabs(), new Converter<TopnewsTab, List<Object[]>>() {
                    @Override
                    public List<Object[]> convert(final TopnewsTab tab) {
                        return Lambda.convert(tab.getNews(), new Converter<TopnewsTabItem, Object[]>() {
                            @Override
                            public Object[] convert(TopnewsTabItem item) {
                                return new Object[]{export, tab.getKey(), item.getI(), item};
                            }
                        });
                    }
                })) {
            res.addAll(o);
        }
        return res;
    }
}
