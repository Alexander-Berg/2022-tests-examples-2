#include <gtest/gtest.h>

#include <stq/tasks/eats_send_receipt_ofd_check.hpp>

TEST(Filter, PersonalDataFilter) {
  std::string json_with_data =
      "{\"code\": 3, \"user\": \"Общество с ограниченной ответственностью "
      "\\\"ЯНДЕКС.ЕДА\\\"\", \"items\": [{\"sum\": 111950, \"name\": \"Расходы "
      "на исполнение поручений по заказу\", \"price\": 111950, \"quantity\": "
      "1.0, \"paymentType\": 4, \"productType\": 1, \"providerInn\": "
      "\"7810351835  \", \"paymentAgentByProductType\": 64}, {\"nds\": 1, "
      "\"sum\": 100, \"name\": \"Услуга по сборке\", \"price\": 100, "
      "\"quantity\": 1.0, \"paymentType\": 4, \"productType\": 1, "
      "\"providerInn\": \"7810351835  \", \"paymentAgentByProductType\": 64}], "
      "\"nds18\": 17, \"ndsNo\": 111950, \"fnsSite\": \"www.nalog.gov.ru\", "
      "\"userInn\": \"9705114405\", \"dateTime\": 1647355260, \"kktRegId\": "
      "\"0000000000000000\", \"totalSum\": 112050, \"creditSum\": 0, "
      "\"fiscalSign\": 932815772, \"prepaidSum\": 0, \"retailPlace\": "
      "\"https://eda.yandex.ru\", \"shiftNumber\": 60, \"cashTotalSum\": 0, "
      "\"provisionSum\": 0, \"taxationType\": 1, \"ecashTotalSum\": 112050, "
      "\"machineNumber\": \"3010001\", \"operationType\": 1, "
      "\"requestNumber\": 2477, \"retailAddress\": \"127410, Москва г, "
      "Алтуфьевское ш, дом № 33Г\", \"paymentAgentType\": 64, "
      "\"fiscalDriveNumber\": \"9960440301940686\", \"messageFiscalSign\": "
      "15047213490960402049, \"buyerPhoneOrAddress\": \"example@mail.ru\", "
      "\"fiscalDocumentNumber\": 229290, \"fiscalDocumentFormatVer\": 2}";
  std::string json_without_data =
      "{\"code\": 3, \"user\": \"Общество с ограниченной ответственностью "
      "\\\"ЯНДЕКС.ЕДА\\\"\", \"items\": [{\"sum\": 111950, \"name\": \"Расходы "
      "на исполнение поручений по заказу\", \"price\": 111950, \"quantity\": "
      "1.0, \"paymentType\": 4, \"productType\": 1, "
      "\"paymentAgentByProductType\": 64}, {\"nds\": 1, \"sum\": 100, "
      "\"name\": \"Услуга по сборке\", \"price\": 100, \"quantity\": 1.0, "
      "\"paymentType\": 4, \"productType\": 1, \"paymentAgentByProductType\": "
      "64}], \"nds18\": 17, \"ndsNo\": 111950, \"fnsSite\": "
      "\"www.nalog.gov.ru\", \"userInn\": \"9705114405\", \"dateTime\": "
      "1647355260, \"kktRegId\": \"0000000000000000\", \"totalSum\": 112050, "
      "\"creditSum\": 0, \"fiscalSign\": 932815772, \"prepaidSum\": 0, "
      "\"retailPlace\": \"https://eda.yandex.ru\", \"shiftNumber\": 60, "
      "\"cashTotalSum\": 0, \"provisionSum\": 0, \"taxationType\": 1, "
      "\"ecashTotalSum\": 112050, \"machineNumber\": \"3010001\", "
      "\"operationType\": 1, \"requestNumber\": 2477, \"retailAddress\": "
      "\"127410, Москва г, Алтуфьевское ш, дом № 33Г\", \"paymentAgentType\": "
      "64, \"fiscalDriveNumber\": \"9960440301940686\", \"messageFiscalSign\": "
      "15047213490960402049, \"fiscalDocumentNumber\": 229290, "
      "\"fiscalDocumentFormatVer\": 2}";
  formats::json::Value value = formats::json::FromString(json_with_data);
  formats::json::Value value_without_data =
      formats::json::FromString(json_without_data);
  std::cout << ToString(value) << std::endl << std::endl;
  stq_tasks::eats_send_receipt_ofd_check::Filter(value);
  std::cout << ToString(value) << std::endl << std::endl;
  std::cout << ToString(value_without_data) << std::endl << std::endl;
  ASSERT_TRUE(value == value_without_data);
}
