package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions.pairs;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ch.lambdaj.collection.LambdaCollections.with;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nonParameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.utils.Utils.makePairs;
import static ru.yandex.autotests.metrika.utils.Utils.makeStringPairs;

/**
 * Created by konkov on 25.08.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Пары измерений по визитам")
@RunWith(Parameterized.class)
public class DimensionPairVisitTest extends DimensionPairsBaseTest {

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection createParameters() {
        return makePairs(
                with(makeStringPairs(
                        VISIT_DIMENSIONS,
                        user.onMetadataSteps().getDimensions(table(TableEnum.VISITS))))
                        .remove(anyOf(
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:goal")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:goalName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interestName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest2d1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest2d2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest2d3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest2Name1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest2Name2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:interest2Name3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productBrand")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCategoryLevel1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCategoryLevel2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCategoryLevel3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCategoryLevel4")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCategoryLevel5")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCurrency")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCurrencyName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productPosition")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productPrice")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productQuantity")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productSum")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productVariant")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:purchaseCount")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:purchaseCoupon")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:purchaseID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:purchaseRevenue")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productNameCart")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productCoupon")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productBrandCart")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:PProductName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:PProductBrand")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:paramsSource")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productIDCart")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:productID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:PProductID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallEventTime")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallRevenue")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCall<currency>Revenue")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallPhoneNumber")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallTalkDuration")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallHoldDuration")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallDuration")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallHoldDurationTillAnswer")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallHoldDurationTillMiss")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallMissed")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallMissedName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallTag")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallFirstTimeCaller")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallFirstTimeCallerName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallURL")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlineCallTrackerURL")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlinePointLocationID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlinePointRegionID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlinePointLocationName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:offlinePointRegionName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanBlock")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanBlockID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanBlockName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanBlockSize")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanIsAdBlock")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanPage")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanPageID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanPageName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrl")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlHash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlHashName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel1Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel2Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel3Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel4")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:yanUrlPathLevel4Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxSite")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxSection")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxPlace")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxBanner")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxBannerType")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxCampaign")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxOwner")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxYanPage")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxYanImp")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxHeaderBidding")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel1Chained")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel2Chained")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel3Chained")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel4Chained")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxPuidKey")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxPuidValue")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxSiteName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxSectionName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxPlaceName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxBannerName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxBannerTypeName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxCampaignName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxOwnerName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxYanPageName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxYanImpName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxHeaderBiddingName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel1Name")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel2Name")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel3Name")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel4Name")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel1ChainedName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel2ChainedName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel3ChainedName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxLevel4ChainedName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxPuidKeyName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxPuidValName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlHash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlHashName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel1Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel2Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel3Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel4")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:adfoxUrlPathLevel4Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:eventInvolvedTime")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherEventTime")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticle")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleAuthors")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleAuthor")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleFromID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleFromTitle")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleHasFullScroll")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleHasFullRead")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleHasRecircled")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleID")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleInvolvedTime")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticlePublishedDate")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleReadPart")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleRubric")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleRubric2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleScrollDown")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleTitle")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleTopics")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleTopic")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleURL")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherPageFormat")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherPageFormatName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherTrafficSource")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherTrafficSourceName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherTrafficSource2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherTrafficSource2Name")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleHasFullReadName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleHasFullScrollName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleHasRecircledName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleReadPartName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherArticleScrollDownName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherLongArticle")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherLongArticleName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:publisherViews")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:vacuumEvent")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:vacuumEventName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:vacuumOrganization")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:vacuumOrganizationName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:vacuumSurface")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:vacuumSurfaceName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURL")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLHash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLHashName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLDomain")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathFull")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPath")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLProto")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel4")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel5")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel1Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel2Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel3Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel4Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWArticleURLPathLevel5Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURL")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLHash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLHashName")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLDomain")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathFull")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPath")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLProto")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel1")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel2")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel3")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel4")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel5")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel1Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel2Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel3Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel4Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWURLPathLevel5Hash")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWConversion")),
                                equalTo(asList("ym:s:paramsLevel1", "ym:s:RWConversionName"))
                                )),
                user.onMetadataSteps().getMetrics(table(TableEnum.VISITS).and(nonParameterized()))
                        .stream().findFirst().get());
    }
}
