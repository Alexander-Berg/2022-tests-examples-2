#pragma once

#include <fstream>
#include <iterator>
#include <mongo/mongo.hpp>
#include <sstream>

namespace bson_utils {

class BSONCompare {
  bool CompareArrays(const std::vector<mongo::BSONElement>& a1,
                     const std::vector<mongo::BSONElement>& a2,
                     std::string path) const {
    if (a1.size() != a2.size()) {
      std::cout << "mismatch: differen size in " << path << std::endl;
      return false;
    }

    for (size_t i = 0; i < a1.size(); ++i) {
      if (!CompareElements(a1[i], a2[i], path + "/" + std::to_string(i))) {
        return false;
      }
    }

    return true;
  }

  bool CompareObjects(const mongo::BSONObj& v1, const mongo::BSONObj& v2,
                      std::string path) const {
    std::set<std::string> v1_fields;
    std::set<std::string> v2_fields;

    v1.getFieldNames(v1_fields);
    v2.getFieldNames(v2_fields);

    if (v1_fields != v2_fields) {
      std::cout << "mismatch: different fields in " << path << std::endl;
      std::cout << "expected: ";
      std::copy(v1_fields.begin(), v1_fields.end(),
                std::ostream_iterator<std::string>(std::cout, " "));
      std::cout << std::endl << "actual: ";
      std::copy(v2_fields.begin(), v2_fields.end(),
                std::ostream_iterator<std::string>(std::cout, " "));
      std::cout << std::endl;
      return false;
    }

    auto it_v1 = v1.begin();
    while (it_v1.more()) {
      auto e1 = it_v1.next();
      auto e2 = v2.getField(e1.fieldName());

      if (!CompareElements(e1, e2, path)) {
        return false;
      }
    }

    return true;
  }

  bool CompareElements(const mongo::BSONElement e1, const mongo::BSONElement e2,
                       std::string path) const {
    if (e1.type() == mongo::BSONType::Object) {
      if (!CompareObjects(e1.Obj(), e2.Obj(), path + "/" + e1.fieldName())) {
        return false;
      }
    } else if (e1.type() == mongo::BSONType::Array) {
      if (!CompareArrays(e1.Array(), e2.Array(), path + "/" + e1.fieldName())) {
        return false;
      }
    } else if (e1.type() == mongo::BSONType::Date) {
      // don't compare dates
    } else {
      if (e1 != e2) {
        std::cout << "mismatch: " << e1 << " != " << e2 << " in ";
        std::cout << path << std::endl;
        return false;
      }
    }
    return true;
  }

 public:
  bool Compare(const mongo::BSONObj& v1, const mongo::BSONObj& v2,
               std::string path = "/") const {
    return CompareObjects(v1, v2, path);
  }
};

inline mongo::BSONObj Load(const std::string& filename) {
  std::ifstream stream(std::string(SOURCE_DIR) + "/tests/static/" + filename);
  assert(stream);
  std::string str((std::istreambuf_iterator<char>(stream)),
                  std::istreambuf_iterator<char>());
  return ::mongo::fromjson(str);
}

}  // namespace bson_utils
