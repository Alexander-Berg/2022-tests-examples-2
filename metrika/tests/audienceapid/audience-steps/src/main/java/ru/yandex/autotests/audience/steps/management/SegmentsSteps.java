package ru.yandex.autotests.audience.steps.management;

import java.io.InputStream;
import java.net.URL;
import java.util.List;
import java.util.function.Predicate;

import org.hamcrest.Matcher;

import ru.yandex.audience.AppMetricaSegment;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.LookalikeSegment;
import ru.yandex.audience.MetrikaSegment;
import ru.yandex.audience.dmp.DmpSegment;
import ru.yandex.audience.geo.CircleGeoSegment;
import ru.yandex.audience.geo.GeoPoint;
import ru.yandex.audience.geo.GeoSegment;
import ru.yandex.audience.geo.PolygonGeoSegment;
import ru.yandex.audience.pixel.PixelSegment;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentClientIdSegmentIdConfirmPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentClientIdSegmentIdConfirmPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdConfirmPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdConfirmPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdDELETESchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdModifyDataPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdPUTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdPUTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdReprocessPUTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdUpdateGeoPointsPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdUpdateGeoPointsPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateAppmetricaPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateAppmetricaPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateDmpPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateDmpPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateDmpsPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateDmpsPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateGeoPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateGeoPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateGeoPolygonPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateGeoPolygonPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateLookalikePOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateLookalikePOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateMetrikaPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreateMetrikaPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreatePixelPOSTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsCreatePixelPOSTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsGETSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentsUploadFilePOSTSchema;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestDmpWrapper;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.ClientIdSegmentRequestUploading;
import ru.yandex.metrika.audience.pubapi.SegmentName;
import ru.yandex.metrika.audience.pubapi.SegmentRequestAppMetrika;
import ru.yandex.metrika.audience.pubapi.SegmentRequestDmp;
import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoCircle;
import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoPolygon;
import ru.yandex.metrika.audience.pubapi.SegmentRequestLookalike;
import ru.yandex.metrika.audience.pubapi.SegmentRequestMetrika;
import ru.yandex.metrika.audience.pubapi.SegmentRequestPixel;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by konkov on 23.03.2017.
 */
public class SegmentsSteps extends HttpClientLiteFacade {

    public SegmentsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }


    public static class Predicates {
        /**
         * @return предикат - "любой", над любым типом
         */
        public static <T> Predicate<T> any() {
            return m -> true;
        }
    }

    @Step("Получить список доступных сегментов")
    public List<BaseSegment> getSegments(IFormParameters... parameters) {
        return getSegments(SUCCESS_MESSAGE, expectSuccess(), parameters).getSegments();
    }

    @Step("Получить список доступных сегментов и ожидать ошибку {0}")
    public List<BaseSegment> getSegmentsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getSegments(ERROR_MESSAGE, expectError(error), parameters).getSegments();
    }

    private V1ManagementSegmentsGETSchema getSegments(String message, Matcher matcher, IFormParameters... parameters) {
        V1ManagementSegmentsGETSchema result =
                get(V1ManagementSegmentsGETSchema.class, "/v1/management/segments", parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Сохранить сегмент {0}, созданный из файла")
    public UploadingSegment confirmSegment(Long segmentId,
                                           SegmentRequestUploading segment,
                                           IFormParameters... parameters) {
        return confirmSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, segment, parameters).getSegment();
    }

    @Step("Сохранить сегмент по ClientId Метрики {0}, созданный из файла")
    public UploadingSegment confirmClientIdSegment(Long segmentId,
                                                   ClientIdSegmentRequestUploading segment,
                                                   IFormParameters... parameters) {
        return confirmClientIdSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, segment, parameters).getSegment();
    }

    @Step("Сохранить сегмент по ClientId Метрики {1}, созданный из файла и ожидать ошибку {0}")
    public UploadingSegment confirmClientIdSegmentAndExpectError(IExpectedError error,
                                                                 Long segmentId,
                                                                 ClientIdSegmentRequestUploading segment,
                                                                 IFormParameters... parameters) {
        return confirmClientIdSegment(ERROR_MESSAGE, expectError(error), segmentId, segment, parameters).getSegment();
    }

    @Step("Сохранить сегмент {1}, созданный из файла и ожидать ошибку {0}")
    public UploadingSegment confirmSegmentAndExpectError(IExpectedError error,
                                                         Long segmentId,
                                                         SegmentRequestUploading segment,
                                                         IFormParameters... parameters) {
        return confirmSegment(ERROR_MESSAGE, expectError(error), segmentId, segment, parameters).getSegment();
    }

    private V1ManagementSegmentSegmentIdConfirmPOSTSchema confirmSegment(String message, Matcher matcher,
                                                                         Long segmentId,
                                                                         SegmentRequestUploading segment,
                                                                         IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdConfirmPOSTSchema result = post(V1ManagementSegmentSegmentIdConfirmPOSTSchema.class,
                format("/v1/management/segment/%s/confirm", segmentId),
                new V1ManagementSegmentSegmentIdConfirmPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    private V1ManagementSegmentClientIdSegmentIdConfirmPOSTSchema confirmClientIdSegment(String message, Matcher matcher,
                                                                                         Long segmentId,
                                                                                         ClientIdSegmentRequestUploading segment,
                                                                                         IFormParameters... parameters) {
        V1ManagementSegmentClientIdSegmentIdConfirmPOSTSchema result = post(V1ManagementSegmentClientIdSegmentIdConfirmPOSTSchema.class,
                format("/v1/management/segment/client_id/%s/confirm", segmentId),
                new V1ManagementSegmentClientIdSegmentIdConfirmPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент с типом «pixel»")
    public PixelSegment createPixel(SegmentRequestPixel segment, IFormParameters... parameters) {
        return createPixel(SUCCESS_MESSAGE, expectSuccess(), segment, parameters).getSegment();
    }

    @Step("Создать сегмент с типом «pixel» и ожидать ошибку {0}")
    public PixelSegment createPixelAndExpectError(IExpectedError error,
                                                  SegmentRequestPixel segment,
                                                  IFormParameters... parameters) {
        return createPixel(ERROR_MESSAGE, expectError(error), segment, parameters).getSegment();
    }

    private V1ManagementSegmentsCreatePixelPOSTSchema createPixel(String message, Matcher matcher,
                                                                  SegmentRequestPixel segment,
                                                                  IFormParameters... parameters) {
        V1ManagementSegmentsCreatePixelPOSTSchema result = post(V1ManagementSegmentsCreatePixelPOSTSchema.class,
                "/v1/management/segments/create_pixel",
                new V1ManagementSegmentsCreatePixelPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент с типом «lookalike»")
    public LookalikeSegment createLookalike(SegmentRequestLookalike segment, IFormParameters... parameters) {
        return createLookalike(SUCCESS_MESSAGE, expectSuccess(), segment, parameters).getSegment();
    }

    @Step("Создать сегмент с типом «lookalike» и ожидать ошибку {0}")
    public LookalikeSegment createLookalikeAndExpectError(IExpectedError error,
                                                          SegmentRequestLookalike segment,
                                                          IFormParameters... parameters) {
        return createLookalike(ERROR_MESSAGE, expectError(error), segment, parameters).getSegment();
    }

    private V1ManagementSegmentsCreateLookalikePOSTSchema createLookalike(String message, Matcher matcher,
                                                                          SegmentRequestLookalike segment,
                                                                          IFormParameters... parameters) {
        V1ManagementSegmentsCreateLookalikePOSTSchema result = post(V1ManagementSegmentsCreateLookalikePOSTSchema.class,
                "/v1/management/segments/create_lookalike",
                new V1ManagementSegmentsCreateLookalikePOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент из объекта метрики")
    public MetrikaSegment createMetrika(SegmentRequestMetrika segment, IFormParameters... parameters) {
        return createMetrika(SUCCESS_MESSAGE, expectSuccess(), segment, parameters).getSegment();
    }

    @Step("Создать сегмент из объекта метрики и ожидать ошибку {0}")
    public MetrikaSegment createMetrikaAndExpectError(IExpectedError error,
                                                      SegmentRequestMetrika segment,
                                                      IFormParameters... parameters) {
        return createMetrika(ERROR_MESSAGE, expectError(error), segment, parameters).getSegment();
    }

    private V1ManagementSegmentsCreateMetrikaPOSTSchema createMetrika(String message, Matcher matcher,
                                                                      SegmentRequestMetrika segment,
                                                                      IFormParameters... parameters) {
        V1ManagementSegmentsCreateMetrikaPOSTSchema result = post(V1ManagementSegmentsCreateMetrikaPOSTSchema.class,
                "/v1/management/segments/create_metrika",
                new V1ManagementSegmentsCreateMetrikaPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент из объекта AppMetrica")
    public AppMetricaSegment createAppMetrica(SegmentRequestAppMetrika segment, IFormParameters... parameters) {
        return createAppMetrica(SUCCESS_MESSAGE, expectSuccess(), segment, parameters).getSegment();
    }

    @Step("Создать сегмент из объекта AppMetrica и ожидать ошибку {0}")
    public AppMetricaSegment createAppMetricaAndExpectError(IExpectedError error,
                                                            SegmentRequestAppMetrika segment,
                                                            IFormParameters... parameters) {
        return createAppMetrica(ERROR_MESSAGE, expectError(error), segment, parameters).getSegment();
    }

    private V1ManagementSegmentsCreateAppmetricaPOSTSchema createAppMetrica(String message, Matcher matcher,
                                                                            SegmentRequestAppMetrika segment,
                                                                            IFormParameters... parameters) {
        V1ManagementSegmentsCreateAppmetricaPOSTSchema result = post(V1ManagementSegmentsCreateAppmetricaPOSTSchema.class,
                "/v1/management/segments/create_appmetrica",
                new V1ManagementSegmentsCreateAppmetricaPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Cоздать сегмент с типом «dmp»: {0}")
    public DmpSegment createDmp(SegmentRequestDmpWrapper segment,
                                IFormParameters... parameters) {
        return createDmp(SUCCESS_MESSAGE, expectSuccess(), segment.get(), parameters).getSegment();
    }

    @Step("Создать сегмент с типом «dmp»: {1} - и ожидать ошибку {0}")
    public DmpSegment createDmpAndExpectError(IExpectedError error,
                                              SegmentRequestDmpWrapper segment,
                                              IFormParameters... parameters) {
        return createDmp(ERROR_MESSAGE, expectError(error), segment.get(), parameters).getSegment();
    }

    private V1ManagementSegmentsCreateDmpPOSTSchema createDmp(String message, Matcher matcher,
                                                              SegmentRequestDmp segment,
                                                              IFormParameters... parameters) {
        V1ManagementSegmentsCreateDmpPOSTSchema result = post(V1ManagementSegmentsCreateDmpPOSTSchema.class,
                "v1/management/segments/create_dmp",
                new V1ManagementSegmentsCreateDmpPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("создать несколько сегментов с типом «dmp»")
    public List<BaseSegment> createDmps(List<SegmentRequestDmp> segments,
                                        IFormParameters... parameters) {
        return createDmps(SUCCESS_MESSAGE, expectSuccess(), segments, parameters).getSegments();
    }

    @Step("создать несколько сегментов с типом «dmp» и ожидать ошибку {0}")
    public List<BaseSegment> createDmpsAndExpectError(IExpectedError error,
                                                      List<SegmentRequestDmp> segments,
                                                      IFormParameters... parameters) {
        return createDmps(ERROR_MESSAGE, expectError(error), segments, parameters).getSegments();
    }

    private V1ManagementSegmentsCreateDmpsPOSTSchema createDmps(String message, Matcher matcher,
                                                                List<SegmentRequestDmp> segments,
                                                                IFormParameters... parameters) {
        V1ManagementSegmentsCreateDmpsPOSTSchema result = post(V1ManagementSegmentsCreateDmpsPOSTSchema.class,
                "v1/management/segments/create_dmps",
                new V1ManagementSegmentsCreateDmpsPOSTRequestSchema().withSegments(segments),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент с типом «геолокация»")
    public CircleGeoSegment createGeo(SegmentRequestGeoCircle segment, IFormParameters... parameters) {
        return createGeo(SUCCESS_MESSAGE, expectSuccess(), segment, parameters).getSegment();
    }

    @Step("Создать сегмент с типом «геолокация»")
    public PolygonGeoSegment createGeo(SegmentRequestGeoPolygon segment, IFormParameters... parameters) {
        return createGeo(SUCCESS_MESSAGE, expectSuccess(), segment, parameters).getSegment();
    }

    @Step("Создать сегмент с типом «геолокация» и ожидать ошибку {0}")
    public CircleGeoSegment createGeoAndExpectError(IExpectedError error,
                                                    SegmentRequestGeoCircle segment,
                                                    IFormParameters... parameters) {
        return createGeo(ERROR_MESSAGE, expectError(error), segment, parameters).getSegment();
    }

    @Step("Создать сегмент с типом «геолокация» и ожидать ошибку {0}")
    public PolygonGeoSegment createGeoAndExpectError(IExpectedError error,
                                                    SegmentRequestGeoPolygon segment,
                                                    IFormParameters... parameters) {
        return createGeo(ERROR_MESSAGE, expectError(error), segment, parameters).getSegment();
    }

    private V1ManagementSegmentsCreateGeoPOSTSchema createGeo(String message, Matcher matcher,
                                                              SegmentRequestGeoCircle segment,
                                                              IFormParameters... parameters) {
        V1ManagementSegmentsCreateGeoPOSTSchema result = post(V1ManagementSegmentsCreateGeoPOSTSchema.class,
                "/v1/management/segments/create_geo",
                new V1ManagementSegmentsCreateGeoPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    private V1ManagementSegmentsCreateGeoPolygonPOSTSchema createGeo(String message, Matcher matcher,
                                                                     SegmentRequestGeoPolygon segment,
                                                                     IFormParameters... parameters) {
        V1ManagementSegmentsCreateGeoPolygonPOSTSchema result = post(V1ManagementSegmentsCreateGeoPolygonPOSTSchema.class,
                "/v1/management/segments/create_geo_polygon",
                new V1ManagementSegmentsCreateGeoPolygonPOSTRequestSchema().withSegment(segment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить список координат сегмента {0} с типом «геолокация»")
    public GeoSegment updateGeoPoints(Long segmentId, List<GeoPoint> points, IFormParameters... parameters) {
        return updateGeoPoints(SUCCESS_MESSAGE, expectSuccess(), segmentId, points, parameters).getSegment();
    }

    @Step("Изменить список координат сегмента {1} с типом «геолокация» и ожидать ошибку {0}")
    public GeoSegment updateGeoPointsAndExpectError(IExpectedError error,
                                                    Long segmentId,
                                                    List<GeoPoint> points,
                                                    IFormParameters... parameters) {
        return updateGeoPoints(ERROR_MESSAGE, expectError(error), segmentId, points, parameters).getSegment();
    }

    private V1ManagementSegmentSegmentIdUpdateGeoPointsPOSTSchema updateGeoPoints(String message,
                                                                                  Matcher matcher,
                                                                                  Long segmentId,
                                                                                  List<GeoPoint> points,
                                                                                  IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdUpdateGeoPointsPOSTSchema result = post(
                V1ManagementSegmentSegmentIdUpdateGeoPointsPOSTSchema.class,
                format("/v1/management/segment/%s/update_geo_point", segmentId),
                new V1ManagementSegmentSegmentIdUpdateGeoPointsPOSTRequestSchema().withPoints(points),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент из файла")
    public UploadingSegment uploadFile(InputStream content, IFormParameters... parameters) {
        return uploadFile(SUCCESS_MESSAGE, expectSuccess(), content, parameters).getSegment();
    }

    @Step("Создать сегмент из многоколоночного CSV-файла")
    public UploadingSegment uploadCsvFile(InputStream content, IFormParameters... parameters) {
        return uploadCsvFile(SUCCESS_MESSAGE, expectSuccess(), content, parameters).getSegment();
    }

    @Step("Создать сегмент из многоколоночного CSV-файла и ожидать ошибку {0}")
    public UploadingSegment uploadCsvFileAndExpectError(IExpectedError error,
                                                        InputStream content,
                                                        IFormParameters... parameters) {
        return uploadCsvFile(ERROR_MESSAGE,expectError(error), content, parameters).getSegment();
    }

    @Step("Создать сегмент из файла и ожидать ошибку {0}")
    public UploadingSegment uploadFileAndExpectError(IExpectedError error,
                                                     InputStream content,
                                                     IFormParameters... parameters) {
        return uploadFile(ERROR_MESSAGE, expectError(error), content, parameters).getSegment();
    }

    private V1ManagementSegmentsUploadFilePOSTSchema uploadFile(String message,
                                                                Matcher matcher,
                                                                InputStream content,
                                                                IFormParameters... parameters) {
        return uploadFileUsingUrl(message, matcher, content, parameters, "/v1/management/segments/upload_file");
    }

    private V1ManagementSegmentsUploadFilePOSTSchema uploadCsvFile(String message,
                                                                   Matcher matcher,
                                                                   InputStream content,
                                                                   IFormParameters... parameters) {
        return uploadFileUsingUrl(message, matcher, content, parameters, "/v1/management/segments/upload_csv_file");
    }

    private V1ManagementSegmentsUploadFilePOSTSchema uploadFileUsingUrl(String message, Matcher matcher, InputStream content, IFormParameters[] parameters, String url) {
        V1ManagementSegmentsUploadFilePOSTSchema result = post(V1ManagementSegmentsUploadFilePOSTSchema.class,
                url,
                content, parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить данные сегмента {0}, созданного из файла")
    public UploadingSegment modifyUploadedFile(Long segmentId, InputStream content, IFormParameters... parameters) {
        return modifyUploadedFile(SUCCESS_MESSAGE, expectSuccess(), segmentId, content, parameters).getSegment();
    }

    @Step("Изменить данные сегмента {1}, созданного из файла и ожидать ошибку {0}")
    public UploadingSegment modifyUploadedFileAndExpectError(IExpectedError error,
                                                             Long segmentId,
                                                             InputStream content,
                                                             IFormParameters... parameters) {
        return modifyUploadedFile(ERROR_MESSAGE, expectError(error), segmentId, content, parameters).getSegment();
    }

    private V1ManagementSegmentSegmentIdModifyDataPOSTSchema modifyUploadedFile(String message, Matcher matcher,
                                                                                Long segmentId, InputStream content,
                                                                                IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdModifyDataPOSTSchema result = post(V1ManagementSegmentSegmentIdModifyDataPOSTSchema.class,
                format("/v1/management/segment/%s/modify_data", segmentId),
                content, parameters);


        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить сегмент {0}")
    public <T extends BaseSegment> T editSegment(Long segmentId, T segment, IFormParameters... parameters) {
        return (T) editSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, segment, parameters).getSegment();
    }

    @Step("Изменить сегмент {1} и ожидать ошибку {0}")
    public <T extends BaseSegment> T editSegmentAndExpectError(IExpectedError error,
                                                               Long segmentId,
                                                               T segment,
                                                               IFormParameters... parameters) {
        return (T) editSegment(ERROR_MESSAGE, expectError(error), segmentId, segment, parameters).getSegment();
    }

    private <T extends BaseSegment> V1ManagementSegmentSegmentIdPUTSchema editSegment(String message, Matcher matcher,
                                                                                      Long segmentId,
                                                                                      T segment,
                                                                                      IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdPUTSchema result = put(V1ManagementSegmentSegmentIdPUTSchema.class,
                format("/v1/management/segment/%s", segmentId),
                new V1ManagementSegmentSegmentIdPUTRequestSchema().withSegment(new SegmentName().withName(segment.getName())),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить сегмент {0}")
    public Boolean deleteSegment(Long segmentId, IFormParameters... parameters) {
        return deleteSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, parameters).getSuccess();
    }

    @Step("Удалить сегмент {0} и игнорировать статус")
    public Boolean deleteSegmentAndIgnoreStatus(Long segmentId, IFormParameters... parameters) {
        if (segmentId != null) {
            return deleteSegment(ANYTHING_MESSAGE, expectAnything(), segmentId, parameters).getSuccess();
        } else {
            return true;
        }
    }

    @Step("Удалить сегмент {1} и ожидать ошибку {0}")
    public Boolean deleteSegmentAndExpectError(IExpectedError error, Long segmentId, IFormParameters... parameters) {
        return deleteSegment(ERROR_MESSAGE, expectError(error), segmentId, parameters).getSuccess();
    }

    private V1ManagementSegmentSegmentIdDELETESchema deleteSegment(String message, Matcher matcher,
                                                                   Long segmentId, IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdDELETESchema result = delete(V1ManagementSegmentSegmentIdDELETESchema.class,
                format("/v1/management/segment/%s", segmentId), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить статистику по сегменту {0}")
    public V1ManagementSegmentSegmentIdStatGETSchema getStat(Long segmentId, IFormParameters... parameters) {
        return getStat(SUCCESS_MESSAGE, expectSuccess(), segmentId, parameters);
    }

    @Step("Получить статистику по сегменту {1} и ожидать ошибку {0}")
    public V1ManagementSegmentSegmentIdStatGETSchema getStatAndExpectError(IExpectedError error,
                                                                           Long segmentId,
                                                                           IFormParameters... parameters) {
        return getStat(ERROR_MESSAGE, expectError(error), segmentId, parameters);
    }

    private V1ManagementSegmentSegmentIdStatGETSchema getStat(String message, Matcher matcher,
                                                              Long segmentId, IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdStatGETSchema result = get(V1ManagementSegmentSegmentIdStatGETSchema.class,
                format("/v1/management/segment/%s/stat", segmentId), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Сохранить список целей для сегмента {0}")
    public V1ManagementSegmentSegmentIdStatPOSTSchema saveGoals(Long segmentId, Long counterId, List<Long> goals,
                                                                IFormParameters... parameters) {
        return saveGoals(SUCCESS_MESSAGE, expectSuccess(), segmentId, counterId, goals, parameters);
    }

    @Step("Сохранить список целей для сегмента {1} и ожидать ошибку {0}")
    public V1ManagementSegmentSegmentIdStatPOSTSchema saveGoalsAndExpectError(IExpectedError error, Long segmentId,
                                                                              Long counterId, List<Long> goals,
                                                                              IFormParameters... parameters) {
        return saveGoals(ERROR_MESSAGE, expectError(error), segmentId, counterId, goals, parameters);
    }

    private V1ManagementSegmentSegmentIdStatPOSTSchema saveGoals(String message, Matcher matcher,
                                                                 Long segmentId, Long counterId, List<Long> goals,
                                                                 IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdStatPOSTSchema result = post(V1ManagementSegmentSegmentIdStatPOSTSchema.class,
                format("/v1/management/segment/%s/stat", segmentId),
                new V1ManagementSegmentSegmentIdStatPOSTRequestSchema().withCounterId(counterId).withGoals(goals),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить список внутренних сегментов")
    public List<BaseSegment> getInternalSegments(IFormParameters... parameters) {
        return getInternalSegments(SUCCESS_MESSAGE, expectSuccess(), parameters).getSegments();
    }

    @Step("Получить список внутренних сегментов и ожидать ошибку {0}")
    public List<BaseSegment> getInternalSegmentsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getInternalSegments(ERROR_MESSAGE, expectError(error), parameters).getSegments();
    }

    private V1ManagementSegmentsGETSchema getInternalSegments(String message, Matcher matcher,
                                                              IFormParameters... parameters) {
        V1ManagementSegmentsGETSchema result =
                get(V1ManagementSegmentsGETSchema.class, "/v1/management/client/segments", parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать внутренний сегмент из файла")
    public UploadingSegment uploadFileForInternal(InputStream content, IFormParameters... parameters) {
        return uploadFileForInternal(SUCCESS_MESSAGE, expectSuccess(), content, parameters).getSegment();
    }

    @Step("Создать внутренний сегмент из файла и ожидать ошибку {0}")
    public UploadingSegment uploadFileForInternalAndExpectError(IExpectedError error, InputStream content,
                                                                IFormParameters... parameters) {
        return uploadFileForInternal(ERROR_MESSAGE, expectError(error), content, parameters).getSegment();
    }

    private V1ManagementSegmentsUploadFilePOSTSchema uploadFileForInternal(String message, Matcher matcher,
                                                                           InputStream content,
                                                                           IFormParameters... parameters) {
        V1ManagementSegmentsUploadFilePOSTSchema result = post(V1ManagementSegmentsUploadFilePOSTSchema.class,
                "/v1/management/client/segments/upload_file", content, parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Сохранить внутренний сегмент {0}, созданный из файла")
    public UploadingSegment confirmClientSegment(Long segmentId, SegmentRequestUploading segment,
                                                 IFormParameters... parameters) {
        return confirmClientSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, segment, parameters).getSegment();
    }

    @Step("Сохранить внутренний сегмент {1}, созданный из файла, и ожидать ошибку {0}")
    public UploadingSegment confirmClientSegmentAndExpectError(IExpectedError error, Long segmentId,
                                                               SegmentRequestUploading segment,
                                                               IFormParameters... parameters) {
        return confirmClientSegment(ERROR_MESSAGE, expectError(error), segmentId, segment, parameters).getSegment();
    }

    private V1ManagementSegmentSegmentIdConfirmPOSTSchema confirmClientSegment(String message, Matcher matcher, Long segmentId,
                                                                               SegmentRequestUploading segment, IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdConfirmPOSTSchema result = post(V1ManagementSegmentSegmentIdConfirmPOSTSchema.class,
                format("/v1/management/client/segment/%s/confirm", segmentId),
                new V1ManagementSegmentSegmentIdConfirmPOSTRequestSchema().withSegment(segment), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить данные сегмента {0}, созданного из файла")
    public UploadingSegment modifyClientSegment(Long segmentId, InputStream content, IFormParameters... parameters) {
        return modifyClientSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, content, parameters).getSegment();
    }

    @Step("Изменить данные сегмента {1}, созданного из файла и ожидать ошибку {0}")
    public UploadingSegment modifyClientSegmentAndExpectError(IExpectedError error, Long segmentId, InputStream content,
                                                              IFormParameters... parameters) {
        return modifyClientSegment(ERROR_MESSAGE, expectError(error), segmentId, content, parameters).getSegment();
    }

    private V1ManagementSegmentSegmentIdModifyDataPOSTSchema modifyClientSegment(String message, Matcher matcher,
                                                                                 Long segmentId, InputStream content,
                                                                                 IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdModifyDataPOSTSchema result = post(V1ManagementSegmentSegmentIdModifyDataPOSTSchema.class,
                format("/v1/management/client/segment/%s/modify_data", segmentId),
                content, parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Переименовать сегмент {0}")
    public UploadingSegment editClientSegment(Long segmentId, UploadingSegment segment, IFormParameters... parameters) {
        return (UploadingSegment) editClientSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, segment, parameters)
                .getSegment();
    }

    @Step("Переименовать сегмент {1} и ожидать ошибку {0}")
    public UploadingSegment editClientSegmentAndExpectError(IExpectedError error, Long segmentId, UploadingSegment segment,
                                                            IFormParameters... parameters) {
        return (UploadingSegment) editClientSegment(ERROR_MESSAGE, expectError(error), segmentId, segment, parameters)
                .getSegment();
    }

    private V1ManagementSegmentSegmentIdPUTSchema editClientSegment(String message, Matcher matcher, Long segmentId,
                                                                    UploadingSegment segment, IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdPUTSchema result = put(V1ManagementSegmentSegmentIdPUTSchema.class,
                format("/v1/management/client/segment/%s", segmentId),
                new V1ManagementSegmentSegmentIdPUTRequestSchema().withSegment(new SegmentName().withName(segment.getName())), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить сегмент {0}")
    public Boolean deleteClientSegment(Long segmentId, IFormParameters... parameters) {
        return deleteClientSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, parameters).getSuccess();
    }

    @Step
    public Boolean deleteClientSegmentAndIgnoreStatus(Long segmentId, IFormParameters... parameters) {
        return deleteClientSegment(ANYTHING_MESSAGE, expectAnything(), segmentId, parameters).getSuccess();
    }

    @Step("Удалить сегмент {1} и ожидать ошибку {0}")
    public Boolean deleteClientSegmentAndExpectError(IExpectedError error, Long segmentId, IFormParameters... parameters) {
        return deleteClientSegment(ERROR_MESSAGE, expectError(error), segmentId, parameters).getSuccess();
    }

    private V1ManagementSegmentSegmentIdDELETESchema deleteClientSegment(String message, Matcher matcher,
                                                                         Long segmentId, IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdDELETESchema result = delete(V1ManagementSegmentSegmentIdDELETESchema.class,
                format("/v1/management/client/segment/%s", segmentId), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Переобработать сегмент {0}")
    public Boolean reprocessSegment(Long segmentId, IFormParameters... parameters) {
        return reprocessSegment(SUCCESS_MESSAGE, expectSuccess(), segmentId, parameters).getSuccess();
    }

    @Step("Переобработать сегмент {1} и ожидать ошибку {0}")
    public Boolean reprocessSegmentAndExpectError(IExpectedError error, Long segmentId, IFormParameters... parameters) {
        return reprocessSegment(ERROR_MESSAGE, expectError(error), segmentId, parameters).getSuccess();
    }

    private V1ManagementSegmentSegmentIdReprocessPUTSchema reprocessSegment(String message, Matcher matcher,
                                                                        Long segmentId, IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdReprocessPUTSchema result = put(V1ManagementSegmentSegmentIdReprocessPUTSchema.class,
                format("/v1/management/segment/%s/reprocess", segmentId), null, parameters);

        assertThat(message, result, matcher);

        return result;
    }
}
