#include <userver/utest/utest.hpp>

#include <atomic>

#include <userver/storages/redis/mock_client_base.hpp>

namespace {

const std::string kKey = "key123";
const std::string kValue1 = "value111";
const std::string kValue2 = "value222";

template <typename MockClient, typename MockTransactionImpl>
class RedisTransactionTest {
 public:
  RedisTransactionTest()
      : RedisTransactionTest(std::make_shared<MockClient>()) {}

  const MockClient& Client() const { return *client_; }
  MockClient& Client() { return *client_; }

 private:
  explicit RedisTransactionTest(std::shared_ptr<MockClient> client)
      : client_(client) {
    client_->template SetMockTransactionImplType<MockTransactionImpl>();
  }

  std::shared_ptr<MockClient> client_;
};

class MockTransactionImplBasic
    : public storages::redis::MockTransactionImplBase {
 public:
  ~MockTransactionImplBasic() {
    EXPECT_EQ(get_counter_, 1);
    EXPECT_EQ(set_counter_, 1);
  }

  storages::redis::RequestGet Get(std::string key) override {
    EXPECT_EQ(set_counter_, 0);
    ++get_counter_;
    EXPECT_EQ(key, kKey);
    return storages::redis::CreateMockRequest<storages::redis::RequestGet>(
        kValue1);
  }

  storages::redis::RequestSet Set(std::string key, std::string value) override {
    EXPECT_EQ(get_counter_, 1);
    ++set_counter_;
    EXPECT_EQ(key, kKey);
    EXPECT_EQ(value, kValue2);
    return storages::redis::CreateMockRequest<storages::redis::RequestSet>();
  }

 private:
  std::atomic<size_t> get_counter_{0};
  std::atomic<size_t> set_counter_{0};
};

}  // namespace

UTEST(MockRedisTransaction, BasicTest) {
  RedisTransactionTest<storages::redis::MockClientBase,
                       MockTransactionImplBasic>
      transaction_test;
  auto& client = transaction_test.Client();

  auto transaction = client.Multi();
  auto get_req = transaction->Get(kKey);
  auto set_req = transaction->Set(kKey, kValue2);
  auto request = transaction->Exec({});

  EXPECT_NO_THROW(request.Get());
  EXPECT_EQ(get_req.Get(), kValue1);
  EXPECT_NO_THROW(set_req.Get());
}

UTEST(MockRedisTransaction, NotStartedTransaction) {
  RedisTransactionTest<storages::redis::MockClientBase,
                       MockTransactionImplBasic>
      transaction_test;
  auto& client = transaction_test.Client();

  auto transaction = client.Multi();
  auto get_req = transaction->Get(kKey);
  auto set_req = transaction->Set(kKey, kValue2);
  EXPECT_THROW(get_req.Get(), storages::redis::NotStartedTransactionException);
}

UTEST(MockRedisTransaction, NotStartedTransaction2) {
  RedisTransactionTest<storages::redis::MockClientBase,
                       MockTransactionImplBasic>
      transaction_test;
  auto& client = transaction_test.Client();

  auto transaction = client.Multi();
  auto get_req = transaction->Get(kKey);
  auto set_req = transaction->Set(kKey, kValue2);
  auto request = transaction->Exec({});

  // call subrequest's Get() before request.Get()
  EXPECT_THROW(get_req.Get(), storages::redis::NotStartedTransactionException);
}

UTEST(MockRedisTransaction, TimeoutTest) {
  class MockTransactionImpl : public storages::redis::MockTransactionImplBase {
   public:
    ~MockTransactionImpl() {
      EXPECT_EQ(get_counter_, 1);
      EXPECT_EQ(set_counter_, 1);
    }

    storages::redis::RequestGet Get(std::string key) override {
      EXPECT_EQ(set_counter_, 0);
      ++get_counter_;
      EXPECT_EQ(key, kKey);
      return storages::redis::CreateMockRequestTimeout<
          storages::redis::RequestGet>();
    }

    storages::redis::RequestSet Set(std::string key,
                                    std::string value) override {
      EXPECT_EQ(get_counter_, 1);
      ++set_counter_;
      EXPECT_EQ(key, kKey);
      EXPECT_EQ(value, kValue2);
      return storages::redis::CreateMockRequest<storages::redis::RequestSet>();
    }

   private:
    std::atomic<size_t> get_counter_{0};
    std::atomic<size_t> set_counter_{0};
  };

  RedisTransactionTest<storages::redis::MockClientBase, MockTransactionImpl>
      transaction_test;
  auto& client = transaction_test.Client();

  auto transaction = client.Multi();
  auto get_req = transaction->Get(kKey);
  auto set_req = transaction->Set(kKey, kValue2);
  auto request = transaction->Exec({});

  EXPECT_THROW(request.Get(), ::redis::RequestFailedException);
}
