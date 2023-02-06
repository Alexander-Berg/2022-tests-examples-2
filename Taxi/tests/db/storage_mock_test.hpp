#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <db/storage.hpp>

namespace db {
class MockStorage : public db::IStorage {
 public:
  MOCK_METHOD(std::optional<helpers::transactions::OrderPayment>,
              FetchOrderPayment, (const std::string& order_id),
              (const, override));
  MOCK_METHOD(void, IncOrderPaymentRetryCount, (const std::string& order_id),
              (const, override));
  MOCK_METHOD(std::optional<models::Order>, FetchOrder,
              (const std::string& order_id), (const, override));
  MOCK_METHOD(std::vector<models::DBItem>, FetchOrderItems,
              (const std::string& order_id), (const, override));
  MOCK_METHOD(std::optional<models::Operation>, FetchOperation,
              (const std::int64_t operation_id), (const, override));
  MOCK_METHOD(std::optional<models::Operation>, FetchOperation,
              (const std::string& order_id, const models::OperationType type),
              (const, override));
  MOCK_METHOD(std::vector<models::Operation>, FetchOperations,
              (const std::string& order_id), (const, override));

  MOCK_METHOD(std::vector<models::ItemPaymentTypeRevision>,
              FetchItemsPaymentTypeByRevision,
              (const std::string& order_id, const std::string& revision_id),
              (const, override));

  MOCK_METHOD(void, InsertRescheduleTask,
              (const std::string& task_id, const std::string& order_id,
               int64_t version),
              (const, override));

  MOCK_METHOD(std::vector<models::RescheduledTaskInfo>,
              FetchRescheduledTasksVersion, (const std::string& order_id),
              (const, override));

  MOCK_METHOD(void, DeleteProcessedRescheduledTask,
              (const std::string& task_id), (const, override));
};
}  // namespace db
