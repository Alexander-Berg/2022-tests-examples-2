#include <simple-zookeeper/redis_zookeeper.hpp>

namespace simple_zookeeper {

class RedisZookeeperTester {
 public:
  RedisZookeeperTester(RedisZookeeper& keeper) : keeper_(keeper) {}

  void UpdateMachinesList() { keeper_.UpdateMachinesList(); }

 private:
  RedisZookeeper& keeper_;
};

}  //  namespace simple_zookeeper
