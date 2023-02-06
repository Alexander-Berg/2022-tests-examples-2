package ru.yandex.metrika.util;

import org.junit.Test;

/**
 * CONV-2805
 * @author orantius
 * @version $Id$
 * @since 7/26/11
 */
public class CompositionUpdateTest {

    // update WV_test_1_0.visits set
    //     /        dayNumber = 1301 ,
    //              startTime = '2011-07-25 12:26:28' ,
    //              pageViews = 24 ,
    //              goalCount = 0 ,
    //              goalIds = '' ,
    //    vvc       refererUriHost = 'market.yandex.ru' ,
    //              refererUriPage = 'http://market.yandex.ru/offers.xml?modelid=7322095&hid=91013&hyperid=7322095&grhow=shop&page=4' ,
    //              landingPage = 'http://sestet.ru/Magazin/brand_acer/ACER-Aspire-One-AOHAPPY2-N578Qyy/?r1=yandext&r2=' ,
    //              exitPage = 'http://sestet.ru/Magazin/wireless-mouse/Sony-VGP-BMS20-B/' ,
    //              trafficSource = 3 ,
    //     \        advEngineId = 12 ,
    //     /        searchPhrase = null ,
    //              searchEngineId = 0 ,
    //              openStatServiceId = null ,
    //              openStatAdId = null ,
    //              openStatCampaignId = null ,
    //              openStatSourceId = null ,
    //     vhc      fromLabel = null ,
    //              utmSource = null ,
    //              utmMedium = null ,
    //              utmCampaign = null ,
    //              utmContent = null ,
    //              utmTerm = null ,
    //     \        pagesMd5 = 'nBoFKQcSxWfoOX-2NNzraA,HMYPqyFPIpDpk9YjGGDcyw,VO-CH68mRCQ05JXiqTdRtw,' ,
    //     vec      activityScore = activityScore + 0 ,
    //     vdc      duration = duration + 946
    // where visitId = 5372241462371971196;

    /*        int count = (visit!=null?1:0)+(user!=null?1:0)+(hit!=null?1:0)+(event!=null?1:0)+(duration!=null?1:0);
        UpdateCommand[] subInserts = new UpdateCommand[count];
        int k = 0;
        if (visit!=null){
            subInserts[k]=visit;
            k++;
        }
        if (user!=null){
            subInserts[k]=user;
            k++;
        }
        if (hit!=null){
            subInserts[k]=hit;
            k++;
        }
        if (event!=null){
            subInserts[k]=event;
            k++;
        }
        if (duration!=null){
            subInserts[k]=duration;
            k++;
        }
        return new CompositionUpdate(subInserts);
*/
    @Test
    public void testGetDescr() throws Exception {
        /*DaemonTableResolverImpl tr = new DaemonTableResolverImpl(1);
        tr.setNumberOfSubLayers(1);
        tr.setResolverPolicy(new DbPerSublayerPolicy());
        tr.setDbPrefix("WV_");

        VisitLog visitLog = mock(VisitLog.class);
        when(visitLog.getStartTime()).thenReturn(1300000000000L);
        when(visitLog.getVisitId()).thenReturn(42L);

        CompositionUpdate cu = new CompositionUpdate(new VisitVisitCommand(visitLog, new GoalParser()),
                new VisitHitCommand(42, mock(HitLog.class), mock(OpenStatManager.class)),
                new VisitEventCommand(42, 100500),
                new VisitDurationCommand(42,100));
        UpdateList ul = new UpdateList(new UpdateType(10000,1301,cu.getDescr(), tr));
        ul.addCommand(cu);
        List<String> strings = ul.asSql(10000);
        System.out.println(strings.get(0));*/
    }


}
