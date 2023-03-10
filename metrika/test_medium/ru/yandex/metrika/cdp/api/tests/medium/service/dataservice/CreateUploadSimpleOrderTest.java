package ru.yandex.metrika.cdp.api.tests.medium.service.dataservice;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.web.multipart.MultipartFile;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.dto.core.SimpleOrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.data.rows.SimpleOrderRow;
import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.cdp.frontend.data.DataService.DEFAULT_SIMPLE_COLUMN_NAME;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public class CreateUploadSimpleOrderTest extends AbstractDataServiceTest {
    List<SimpleOrderUpdate> simpleOrdersFromFile;
    OrderUpdate firstOrderUpdateFromLb;
    OrderUpdate secondOrderUpdateFromLb;

    @Before
    public void testBody() {
        int counterId = getCounterId();
        byte[] fileContent = IOUtils
                .resourceAsString(CreateUploadContactsCsvTest.class, "./csv/test_simple_orders.csv").getBytes();
        MultipartFile multipartFileWithOrders = new MockMultipartFile("Simple_Orders.csv", fileContent);
        counterBefore = cdpCountersDao.getCounter(counterId);

        hasFeatureBefore = featureService.getFeatures(counterId).contains(Feature.cdp);

        uploadingMeta = dataService.uploadSimpleOrdersCsv(
                counterId,
                UpdateType.APPEND,
                DelimiterType.SEMICOLON,
                multipartFileWithOrders
        );

        simpleOrdersFromFile = parseUpdateRows(DEFAULT_SIMPLE_COLUMN_NAME,
                multipartFileWithOrders,
                EntityNamespace.SIMPLE_ORDER,
                SimpleOrderRow.class,
                uploadingMeta.getUploadingId(),
                uploadingMeta.getUpdateType());

        var orders = readEntityFromLb(ordersSyncConsumer,
                orderUpdateProtoSerializer,
                uploadingMeta.getUploadingId(),
                3);

        firstOrderUpdateFromLb = orders.get(0);
        secondOrderUpdateFromLb = orders.get(1);
        counter = cdpCountersDao.getCounter(counterId);

        hasFeature = featureService.getFeatures(counterId).contains(Feature.cdp);
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<>(
                Arrays.asList(
                        new Object[][]{
                                {c(test -> assertEquals(Integer.valueOf(3), test.uploadingMeta.getElementsCount())),
                                        "???????? ???????????????????? ?????????????????????? ??????????????"},
                                {c(test -> assertEquals(UploadingFormat.CSV, test.uploadingMeta.getUploadingFormat())),
                                        "???????? ?????????????? ?????????????????????? ????????????"},
                                {c(test -> assertNotNull(test.firstOrderUpdateFromLb)),
                                        "???????????????? ???? nullability ?????????????? ???????????????????????? ????????????"},
                                {c(test -> assertEqualUpdates(test.firstOrderUpdateFromLb, test.simpleOrdersFromFile.get(0).getOrderUpdate())),
                                        "???????? ?????????????? ???????????????????????? ????????????"},
                                {c(test -> assertNotNull(test.secondOrderUpdateFromLb)),
                                        "???????????????? ???? nullability ?????????????? ???????????????????????? ????????????"},
                                {c(test -> assertEqualUpdates(test.secondOrderUpdateFromLb, test.simpleOrdersFromFile.get(1).getOrderUpdate())),
                                        "???????? ?????????????? ???????????????????????? ????????????"},
                                {c(test -> assertEquals((Long) 100L, test.counter.getCdpOrderInProgressGoalId())),
                                        "???????? cdpOrderInProgressGoalId"},
                                {c(test -> assertEquals((Long) 200L, test.counter.getCdpOrderPaidGoalId())),
                                        "???????? cdpOrderPaidGoalId"},
                                {c(test -> assertTrue(test.counter.isHasContacts())), "???????? ???????????????????? ?????????????????? ?? ????????????????"},
                                {c(test -> assertTrue(test.counter.isHasOrders())), "???????? ?????????????? ?????????????? ?? ????????????????"},
                                {c(test -> assertFalse(test.counter.isHasProducts())), "???????? ?????????????? ?????????????????? ?? ????????????????"}
                        }
                ));
        result.addAll(getCommonParameters());
        return result;
    }

    private static Consumer<CreateUploadSimpleOrderTest> c(Consumer<CreateUploadSimpleOrderTest> x) {
        return x;
    }
}
