package ru.yandex.metrika.segments.core.parser.filter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.lang3.tuple.Pair;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.parser.FilterParser;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.filter.Quantifier;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.collections.F;

/**
 * Created by orantius on 27.05.16.
 */
public class Converter21499 {

    static Map<String, String> f = new HashMap<>();
    static {
        f.put("ym:s:ageInterval","ym:u:ageInterval");
        f.put("ym:ad:ageInterval","ym:u:ageInterval");
        f.put("ym:s:gender","ym:u:gender");
        f.put("ym:ad:gender","ym:u:gender");
        f.put("ym:s:firstVisitDate","ym:u:userFirstVisitDate");
        f.put("ym:s:interest","ym:u:interest");
        f.put("ym:s:isRobot","ym:u:isRobot");
        f.put("ym:s:firstAdvEngine","ym:u:firstAdvEngine");
        f.put("ym:s:firstDirectBannerGroup","ym:u:firstDirectBannerGroup");
        f.put("ym:s:firstDirectBannerText","ym:u:firstDirectBannerText");
        f.put("ym:s:firstDirectClickBanner","ym:u:firstDirectClickBanner");
        f.put("ym:s:firstDirectClickOrder","ym:u:firstDirectClickOrder");
        f.put("ym:s:firstDirectConditionType","ym:u:firstDirectConditionType");
        f.put("ym:s:firstDirectPhraseOrCond","ym:u:firstDirectPhraseOrCond");
        f.put("ym:s:firstDirectPlatform","ym:u:firstDirectPlatform");
        f.put("ym:s:firstDirectPlatformType","ym:u:firstDirectPlatformType");
        f.put("ym:s:firstDirectSearchPhrase","ym:u:firstDirectSearchPhrase");
        f.put("ym:s:firstDisplayCampaign","ym:u:firstDisplayCampaign");
        f.put("ym:s:firstFrom","ym:u:firstFrom");
        f.put("ym:s:firstHasGCLID","ym:u:firstHasGCLID");
        f.put("ym:s:firstOpenstatAd","ym:u:firstOpenstatAd");
        f.put("ym:s:firstOpenstatCampaign","ym:u:firstOpenstatCampaign");
        f.put("ym:s:firstOpenstatService","ym:u:firstOpenstatService");
        f.put("ym:s:firstOpenstatSource","ym:u:firstOpenstatSource");
        f.put("ym:s:firstReferalSource","ym:u:firstReferalSource");
        f.put("ym:s:firstSearchEngine","ym:u:firstSearchEngine");
        f.put("ym:s:firstSearchEngineRoot","ym:u:firstSearchEngineRoot");
        f.put("ym:s:firstSearchPhrase","ym:u:firstSearchPhrase");
        f.put("ym:s:firstSocialNetwork","ym:u:firstSocialNetwork");
        f.put("ym:s:firstSocialNetworkProfile","ym:u:firstSocialNetworkProfile");
        f.put("ym:s:firstTrafficSource","ym:u:firstTrafficSource");
        f.put("ym:s:firstUTMCampaign","ym:u:firstUTMCampaign");
        f.put("ym:s:firstUTMContent","ym:u:firstUTMContent");
        f.put("ym:s:firstUTMMedium","ym:u:firstUTMMedium");
        f.put("ym:s:firstUTMSource","ym:u:firstUTMSource");
        f.put("ym:s:firstUTMTerm","ym:u:firstUTMTerm");
        f.put("ym:ad:firstDirectBannerGroup","ym:u:firstDirectBannerGroup");
        f.put("ym:ad:firstDirectBannerText","ym:u:firstDirectBannerText");
        f.put("ym:ad:firstDirectBanner","ym:u:firstDirectClickBanner");
        f.put("ym:ad:firstDirectOrder","ym:u:firstDirectClickOrder");
        f.put("ym:ad:firstDirectConditionType","ym:u:firstDirectConditionType");
        f.put("ym:ad:firstDirectPhraseOrCond","ym:u:firstDirectPhraseOrCond");
        f.put("ym:ad:firstDirectPlatform","ym:u:firstDirectPlatform");
        f.put("ym:ad:firstDirectPlatformType","ym:u:firstDirectPlatformType");
        f.put("ym:ad:firstDirectSearchPhrase","ym:u:firstDirectSearchPhrase");
    }
    /**
     * xxx = a OR xxx = b => (EXISTS ym:u:userID WITH (yyy = a OR yyy = b))
     *
     * xxx = a AND xxx = b => (EXISTS ym:u:userID WITH (yyy = a)) AND (EXISTS ym:u:userID WITH (yyy = b))
     *
     * xxx = a => (EXISTS ym:u:userID WITH (yyy = a))
     */

    public static void main(String[] args) throws Exception {
        Converter21499 converter21499 = new Converter21499();
        converter21499.convert();
    }


    public void convert() throws Exception {
        //MySqlJdbcTemplate conv = AllDatabases.getTemplate("localhost", 3309, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_new"), "conv_main"); //dev
        // MySqlJdbcTemplate conv = AllDatabases.getTemplate("localhost", 3311, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main"); // ts
        MySqlJdbcTemplate conv = AllDatabases.getTemplate("localhost", 3312, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main"); // prod
        ApiUtils apiUtils = FilterParserBraces2Test.getApiUtils(conv);
        FilterParser filterParser = apiUtils.getFilterParser();

        List<Pair<Integer,String>> expressions = conv.query("select segment_id,  expression from segments where status ='active' ", (rs,i) -> Pair.of(rs.getInt(1),rs.getString(2)));
        for (Pair<Integer,String> expression : expressions) {
            for (String s : f.keySet()) {
                if(expression.getRight()!=null && expression.getRight().contains(s)) {
                    //  (ym:s:firstAdvEngine=='ya_direct' or ym:s:firstAdvEngine=='ya_direct_unaccounted') and (ym:s:advEngine!='ya_direct' and ym:s:advEngine!='ya_direct_unaccounted' and ym:s:advEngine!='ya_market' and ym:s:advEngine!='google_adwords' and ym:s:advEngine!='target_mail_ru')
                    String transformed = transform(expression.getRight(), apiUtils, (FilterParserBraces2)filterParser);
                    int update = conv.update("update segments set expression = ? where segment_id = ?", transformed, expression.getLeft());
                    System.out.println("update = " + update);
                }
            }
        }

        System.out.println("end ");
    }

    private static String transform(String expression, ApiUtils apiUtils, FilterParserBraces2 filterParser) {
        System.out.println("expression = " + expression);
        QueryContext global = QueryContext.global("ru", "");

        /*HashMap<String, int[]> idsByName = new HashMap<>();
        idsByName.put(TableSchemaSite.COUNTER_ID, new int[]{expression.getLeft()});
        global = QueryContext.newBuilder(global).apiUtils(apiUtils)
                .tableSchema(apiUtils.getTableSchema())
                .idsByName(idsByName)
                .startDate("2016-01-01")
                .endDate("2016-01-01")
                .userType(UserType.MANAGER)
                .targetTable(TableSchemaSite.VISITS)
                .build();*/
        FBFilter filter = filterParser.parseStringWithANTLR(expression);
        filter = FBFilterTransformers.flattenCompound(filter);

        filter = transformLeaf(filter, apiUtils);
        filter = mergeOr(filter, apiUtils);

        String result = FBFilterTransformers.printFilter(filter);
        System.out.println("" + result);
        return result;
    }

    private static FBFilter mergeOr(FBFilter arg, ApiUtils apiUtils) {
        FBFilterTransformer merger = new FBFilterTransformer() {
            @Override
            public FBFilter visit(FBQuantifierFilter expr) {
                return expr;
            }

            @Override
            public FBFilter visit(FBLeafFilter expr) {
                return expr;
            }

            @Override
            public FBFilter visit(FBOrFilter expr) {
                Map<Boolean, List<FBFilter>> collect = expr.children.stream().collect(Collectors.partitioningBy(f -> isUsercentric(f)));
                Map<String, List<FBFilter>> grouped = collect.get(Boolean.TRUE).stream()
                        .collect(Collectors.groupingBy(f -> ((FBLeafFilter) ((FBQuantifierFilter) f).child).getSelectPart().toString()));
                List<FBFilter> children = new ArrayList<>();
                children.addAll(collect.get(Boolean.FALSE));
                for (List<FBFilter> filters : grouped.values()) {
                    if(filters.size()==1) {
                        children.add(filters.get(0));
                    } else {
                        FBQuantifierFilter qf = new FBQuantifierFilter(Quantifier.EXISTS,
                                                        Collections.singletonList(new FBIdentifier("ym:u:", "specialUser")),
                                                        new FBOrFilter(F.map(filters,  f->((FBQuantifierFilter) f).child)));
                        qf.joinIdsParsed = Collections.singletonList(apiUtils.getUnionBundle().getByApiName().get("ym:u:specialUser"));
                        children.add(qf);
                    }
                }
                return new FBOrFilter(children);
            }

            private boolean isUsercentric(FBFilter f) {
                boolean b = f instanceof FBQuantifierFilter;
                if(b) {
                    FBQuantifierFilter qf = (FBQuantifierFilter)f;
                    return qf.quantifier == Quantifier.EXISTS && qf.joinIds.size()==1&&
                            qf.joinIds.get(0).toString().equals("ym:u:specialUser") && qf.child instanceof FBLeafFilter;
                }
                return false;
            }
        };
        return arg.visit(merger);
    }

    private static FBFilter transformLeaf(FBFilter arg, ApiUtils apiUtils) {
        FBFilterTransformer addQuantor = new FBFilterTransformer() {
            @Override
            public FBFilter visit(FBQuantifierFilter expr) {
                return expr;
            }

            @Override
            public FBFilter visit(FBLeafFilter expr) {
                if(f.containsKey(expr.getSelectPart().toString())) {
                    String id = f.get(expr.getSelectPart().toString());
                    String ns = id.substring(0, id.lastIndexOf(':') + 1);
                    FBLeafFilter ff = new FBLeafFilter(new FBIdentifier(ns, id.substring(ns.length())), expr.getRelation(), expr.getValues());
                    FBQuantifierFilter qf = new FBQuantifierFilter(Quantifier.EXISTS, Collections.singletonList(new FBIdentifier("ym:u:", "specialUser")), ff);
                    qf.joinIdsParsed = Collections.singletonList(apiUtils.getUnionBundle().getByApiName().get("ym:u:specialUser"));
                    return qf;
                }
                return expr;
            }
        };
        return arg.visit(addQuantor);
    }
}
