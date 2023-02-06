#pragma once

#include <string>

namespace testing_environment_context {

const std::string kCreateMarketExpressOrder = R"(
    <root>
        <token></token>
        <uniq>fP0fbpZ9Edzd3a1iw4gnMda1kGOnPw5Y</uniq>
        <hash>fP0fbpZ9Edzd3a1iw4gnMda1kGOnPw5Y</hash>
        <request type="createOrder">
            <order>
                <orderId>
                    <yandexId>{request_id}</yandexId>
                </orderId>
                <locationFrom>
                    <country>Россия</country>
                    <region>Москва и Московская область</region>
                    <locality>Москва</locality>
                    <settlement>Москва</settlement>
                    <street>улица Льва Толстого</street>
                    <house>16</house>
                    <zipCode>123412</zipCode>
                    <lat>55.733969</lat>
                    <lng>37.587093</lng>
                    <locationId>213</locationId>
                </locationFrom>
                <warehouseFrom>
                    <id>
                        <yandexId>10000981168</yandexId>
                        <deliveryId>53</deliveryId>
                        <partnerId>53</partnerId>
                    </id>
                    <address>
                        <country>Россия</country>
                        <region>Москва и Московская область</region>
                        <locality>Москва</locality>
                        <settlement>Москва</settlement>
                        <street>улица Льва Толстого</street>
                        <house>16</house>
                        <zipCode>123412</zipCode>
                        <lat>55.733969</lat>
                        <lng>37.587093</lng>
                        <locationId>213</locationId>
                    </address>
                    <schedule>
                        <workTime>
                            <day>1</day>
                            <periods>
                                <timeInterval>09:00:00+03:00/23:59:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>2</day>
                            <periods>
                                <timeInterval>00:01:00+03:00/23:59:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>3</day>
                            <periods>
                                <timeInterval>09:00:00+03:00/21:00:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>4</day>
                            <periods>
                                <timeInterval>09:00:00+03:00/21:00:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>5</day>
                            <periods>
                                <timeInterval>09:00:00+03:00/21:00:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>6</day>
                            <periods>
                                <timeInterval>09:00:00+03:00/20:00:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>7</day>
                            <periods>
                                <timeInterval>09:00:00+03:00/21:00:00+03:00</timeInterval>
                            </periods>
                        </workTime>
                    </schedule>
                    <phones>
                        <phone>
                            <phoneNumber>+79151005429</phoneNumber>
                        </phone>
                    </phones>
                    <instruction>идти прямо от метро</instruction>
                </warehouseFrom>
                <locationTo>
                    <country>Россия</country>
                    <federalDistrict>Центральный федеральный округ</federalDistrict>
                    <region>Москва и Московская область</region>
                    <locality>Москва</locality>
                    <street>Льва Толстого</street>
                    <house>16</house>
                    <room>303</room>
                    <zipCode>119021</zipCode>
                    <intercom>007</intercom>
                    <porch>404</porch>
                    <floor>8</floor>
                    <metro>Парк Культуры</metro>
                    <lat>55.73397404565889</lat>
                    <lng>37.587092522460836</lng>
                    <locationId>213</locationId>
                </locationTo>
                <weight>1</weight>
                <length>12</length>
                <width>10</width>
                <height>11</height>
                <cargoType>0</cargoType>
                <cargoCost>890</cargoCost>
                <assessedCost>890</assessedCost>
                <paymentMethod>2</paymentMethod>
                <tariff>Такси и Лавки</tariff>
                <deliveryType>0</deliveryType>
                <deliveryCost>49</deliveryCost>
                <deliveryDate>{delivery_date}</deliveryDate>
                <deliveryInterval>18:00:00+03:00/19:00:00+03:00</deliveryInterval>
                <total>0</total>
                <amountPrepaid>939</amountPrepaid>
                <pickupPointId>
                    <yandexId>10000981168</yandexId>
                </pickupPointId>
                <items>
                    <item>
                        <article>217172403.alisa3p</article>
                        <name>Кукла Barbie Черно-белый твидовый костюм, 29 см, DWF54</name>
                        <count>1</count>
                        <price>890</price>
                        <taxes>
                            <tax>
                                <type>VAT</type>
                                <value>7</value>
                            </tax>
                        </taxes>
                        <cargoTypes>
                            <cargoType>980</cargoType>
                            <cargoType>950</cargoType>
                        </cargoTypes>
                        <categoryName>Куклы и пупсы</categoryName>
                        <korobyte>
                            <width>10</width>
                            <height>11</height>
                            <length>12</length>
                            <weightGross>1</weightGross>
                        </korobyte>
                        <unitId>
                            <vendorId>10427354</vendorId>
                            <article>217172403.alisa3p</article>
                        </unitId>
                        <supplier>
                            <inn>3327123849</inn>
                        </supplier>
                    </item>
                </items>
                <recipient>
                    <fio>
                        <name>первоеимя</name>
                        <surname>последнееимя</surname>
                        <patronymic>среднееимя</patronymic>
                    </fio>
                    <phones>
                        <phone>
                            <phoneNumber>+78887776655</phoneNumber>
                        </phone>
                    </phones>
                    <email>ymail@y.mail</email>
                    <uid>851268023</uid>
                </recipient>
                <sender>
                    <id>
                        <yandexId>431782</yandexId>
                    </id>
                    <incorporation>ИП Саванеев Вячеслав Владимирович</incorporation>
                    <phones>
                        <phone>
                            <phoneNumber>+74957392222</phoneNumber>
                        </phone>
                    </phones>
                    <name>Яндекс.Маркет</name>
                    <legalForm>2</legalForm>
                    <inn>657145109813</inn>
                    <taxation>1</taxation>
                    <url>pokupki.market.yandex.ru</url>
                    <ogrn>111111111111111</ogrn>
                </sender>
                <warehouse>
                    <id>
                        <yandexId>10000004403</yandexId>
                        <deliveryId>172</deliveryId>
                        <partnerId>172</partnerId>
                    </id>
                    <address>
                        <country>Россия</country>
                        <region>Московская область</region>
                        <locality>Софьино</locality>
                        <settlement>Софьино</settlement>
                        <street>территория Логистический технопарк Софьино</street>
                        <house>к1</house>
                        <building></building>
                        <housing></housing>
                        <room></room>
                        <zipCode>140126</zipCode>
                        <lat>55.499346</lat>
                        <lng>38.17672</lng>
                        <locationId>120013</locationId>
                    </address>
                    <schedule>
                        <workTime>
                            <day>1</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>2</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>3</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>4</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>5</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>6</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                        <workTime>
                            <day>7</day>
                            <periods>
                                <timeInterval>00:00:00+03:00/23:59:59+03:00</timeInterval>
                            </periods>
                        </workTime>
                    </schedule>
                    <contact>
                        <name>Антон</name>
                        <surname>Сачков</surname>
                    </contact>
                    <phones>
                        <phone>
                            <phoneNumber>+79269900526</phoneNumber>
                        </phone>
                    </phones>
                    <instruction>140126, Московская область, Раменский район, Софьинское сельское поселение, село Софьино, территория Логистический технопарк Софьино, к1</instruction>
                </warehouse>
                <services>
                    <service>
                        <code>
                            <yandexId>CHECK</yandexId>
                            <deliveryId>CHECK</deliveryId>
                            <partnerId>CHECK</partnerId>
                        </code>
                        <isOptional>false</isOptional>
                        <cost>0.0</cost>
                    </service>
                    <service>
                        <code>
                            <yandexId>DELIVERY</yandexId>
                            <deliveryId>DELIVERY</deliveryId>
                            <partnerId>DELIVERY</partnerId>
                        </code>
                        <isOptional>false</isOptional>
                        <cost>0.0</cost>
                        <taxes>
                            <tax>
                                <type>VAT</type>
                                <value>7</value>
                            </tax>
                        </taxes>
                    </service>
                    <service>
                        <code>
                            <yandexId>INSURANCE</yandexId>
                            <deliveryId>INSURANCE</deliveryId>
                            <partnerId>INSURANCE</partnerId>
                        </code>
                        <isOptional>false</isOptional>
                        <cost>0.0</cost>
                    </service>
                    <service>
                        <code>
                            <yandexId>RETURN_SORT</yandexId>
                            <deliveryId>RETURN_SORT</deliveryId>
                            <partnerId>RETURN_SORT</partnerId>
                        </code>
                        <isOptional>false</isOptional>
                        <cost>0.0</cost>
                    </service>
                </services>
                <comment>Оставить у двери</comment>
                <tags>
                    <tag>EXPRESS</tag>
                </tags>
            </order>
            <restrictedData>
                <transferCodes>
                    <inbound>
                        <verification>96429</verification>
                    </inbound>
                </transferCodes>
            </restrictedData>
        </request>
    </root>
)";

inline clients::logistic_platform_uservices::UpsertEmployerRequest
BuildEmployerData(const std::string& employer_code) {
  using namespace clients::logistic_platform_uservices;
  RegistryObject registry;
  registry.config_template = "nespresso";
  registry.separator = ",";

  BrandNameStructure brand_name_new;
  brand_name_new.brand_name_ru = "тикток";
  brand_name_new.brand_name_eng = "tiktok";
  brand_name_new.legal_name = "some legal name";
  brand_name_new.brand_name_genitive = "name in genitive";

  EmployerMeta employer_meta;
  employer_meta.default_inn = "9876543214";
  employer_meta.ndd_route_policy = "strizh_only";
  employer_meta.registry = registry;
  employer_meta.brand_name_new = brand_name_new;
  employer_meta.has_advanced_billing = true;

  UpsertEmployerRequest employer_data;
  employer_data.employer_type = EmployerType::kDefault;
  employer_data.employer_code = employer_code;
  employer_data.employer_meta = employer_meta;

  return employer_data;
}

}  // namespace testing_environment_context
