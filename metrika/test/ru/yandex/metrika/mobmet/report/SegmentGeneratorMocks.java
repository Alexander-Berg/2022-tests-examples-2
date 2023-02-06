package ru.yandex.metrika.mobmet.report;

import ru.yandex.metrika.mobmet.push.common.campaigns.dao.PushApiCampaignsDao;
import ru.yandex.metrika.mobmet.push.common.campaigns.dao.PushCampaignsDao;
import ru.yandex.metrika.mobmet.push.service.PushCampaignMetaService;

import static org.mockito.Mockito.mock;

public class SegmentGeneratorMocks {

    public static PushCampaignMetaService emptyPushMetaService() {
        PushCampaignsDao campaignsDao = mock(PushCampaignsDao.class);
        PushApiCampaignsDao apiCampaignsDao = mock(PushApiCampaignsDao.class);
        PushCampaignMetaService pushService = new PushCampaignMetaService(campaignsDao, apiCampaignsDao);
        pushService.init();
        return pushService;
    }
}
