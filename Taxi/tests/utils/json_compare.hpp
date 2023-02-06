#pragma once

class JSONCompare {
  bool CompareArrays(const Json::Value& v1, const Json::Value& v2,
                     std::string path) {
    if (v1.size() != v2.size()) {
      printf(" arrs mismatch: different sizes at %s\n", path.c_str());
      return false;
    }
    std::vector<Json::Value> c1(v1.begin(), v1.end());
    std::vector<Json::Value> c2(v2.begin(), v2.end());

    std::sort(c1.begin(), c1.end());
    std::sort(c2.begin(), c2.end());

    for (unsigned int i = 0; i < v1.size(); ++i) {
      if (!Compare(c1[i], c2[i], path + std::to_string(i) + "/")) {
        printf("arr mismatch\n");
        return false;
      }
    }
    return true;
  }

  bool CompareObjects(const Json::Value& v1, const Json::Value& v2,
                      std::string path) {
    const auto mn = v1.getMemberNames();
    const auto mn2 = v2.getMemberNames();

    if (mn.size() != mn2.size()) {
      printf("mismatch: different sizes at %s \n", path.c_str());
      return false;
    }

    for (const auto& i : mn) {
      // do not compare image urls, they are not unique and differ from env to
      // env
      if (i == "url" || i == "path") continue;
      if (!Compare(v1[i], v2[i], path + i + "/")) {
        return false;
      }
    }

    return true;
  }

 public:
  bool Compare(const Json::Value& v1, const Json::Value& v2,
               std::string path = "/") {
    if (v1.isArray() && v2.isArray()) {
      return CompareArrays(v1, v2, path);
    } else if (v1.isObject() && v2.isObject()) {
      return CompareObjects(v1, v2, path);
    }
    bool equal = (v1 == v2) || (v1.isIntegral() && v2.isIntegral() &&
                                (v1.asInt() == v2.asInt()));
    if (!equal) {
      printf("Mismatching values: %s %s  at %s\n", v1.toStyledString().c_str(),
             v2.toStyledString().c_str(), path.c_str());
    }
    return equal;
  }

  template <class F>
  bool CheckAll(const F& f, const Json::Value v1) {
    if (v1.isArray()) {
      for (const auto x : v1) {
        if (!f(x)) return false;
        if (!CheckAll(f, x)) return false;
      }
    } else if (v1.isObject()) {
      for (const auto x : v1.getMemberNames()) {
        if (!f(v1[x])) return false;
        if (!CheckAll(f, v1[x])) return false;
      }
    }
    return f(v1);
  }
};
