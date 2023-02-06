"use strict";
function* __pipeline_perform__(__ctx__) {
  function __fetch_resources__(fetch_args) {
    let resources_request = {};
    for (let field in fetch_args) {
      if (!(field in __ctx__.__resource_name_by_field__)) {
        throw 'no resource with field ' + field + ' defined';
      }
      resources_request[field] = {
        name: __ctx__.__resource_name_by_field__[field],
        args: fetch_args[field]
      };
    }
    let instances = __get_mocked_resources__(resources_request, __ctx__.__test__, __ctx__.__testcase__);
    __ctx__.__resource__.__extend__(instances);
  }
  {
    // [fetch stage] fetch_surge_zone
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.fetch_surge_zone = { status: 1 };
    let __stage_meta__ = __stages_meta__.fetch_surge_zone;
    try {
      __on_stage_enter__("fetch_surge_zone");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let point = __ctx__.__input__?.point_a;
      const __fetch_args__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [fetch stage] user code begin
// using base_class and base_class_rule here;
return {
  surge_zone: {point: [0,0]},
  surge_experiment: {point: [0,0]},
};

        // [fetch stage] user code end
      })();
      __stage_meta__.status = 0;
      __set_logging_region__("native_code", __stage_context__);
      yield __fetch_args__;
      __rethrow_resource_fetch_exception__();
    } finally {
      __on_stage_exit__();
    }
  }
  {
    // [logic stage] stage5
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage5 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage5;
    try {
      __on_stage_enter__("stage5");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      for (let class_name in __ctx__.__resource__?.surge_experiment?.rules || {}) {
        let rule = __ctx__.__resource__?.surge_experiment?.rules[class_name];
        __stage_context__.class_name = class_name;
        const __tx_payload__ = (function(){
          __set_logging_region__("user_code", __stage_context__);
          // [logic stage] user code begin
// using class_name, rule and base_class here;
          // [logic stage] user code end
        })();
        if (typeof __tx_payload__ !== 'object') {
          throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
        }
        ++__stage_context__.__iteration_idx__;
        // set status "passed"
        __stage_meta__.status = 0;
      }
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } finally {
      __on_stage_exit__();
    }
  }
  function __check_output__(output, __test__, __testcase__) {
    function assert(__condition__, __message__) {
      if(!__condition__) {
        throw 'Assertion failed in testcase ' + __test__ + '.' + __testcase__ + ': ' + __message__;
      }
    }
    function assert_eq(__obj__, __expected__, __addtitional_properties__ = false, __path__ = []) {
      if (!__expected__ || !__obj__) {
        assert(__expected__ === __obj__, 'differ in path "' + __path__.join('.') + '": \n+  ' + JSON.stringify(__expected__) + '\n-  ' + JSON.stringify(__obj__));
        return;
      }
      if (!(__expected__ instanceof Object)) {
        assert(__expected__ === __obj__, 'differ in path "' + __path__.join('.') + '": \n+  ' + JSON.stringify(__expected__) + '\n-  ' + JSON.stringify(__obj__));
        return;
      }
      assert(__is_array__(__expected__) == __is_array__(__obj__), 'different types for "' + __path__.join('.') + '":\n+  ' + JSON.stringify(__expected__) + '\n-  ' + JSON.stringify(__obj__));
      let __seen__ = new Set();
      for (var __prop__ in __expected__) {
        if (__prop__ instanceof Function) {
          assert((__prop__)(__obj__), 'functional check failed: for ' + __path__.join('.') + '\n  value: ' + JSON.stringify(__obj__) + '\n  fn: ' + __prop__.toString());
        } else if (__prop__ == '__js__') {
          let __check_fn__ = __expected__['__js__'];
          assert(typeof __check_fn__ == 'string', __path__.join('.') + '.__js__ is not a string');
          assert(eval(__check_fn__)(__obj__), 'functional check failed: for ' + __path__.join('.') + '\n  value: ' + JSON.stringify(__obj__) + '\n  fn: ' + __check_fn__);
        } else if (__expected__.hasOwnProperty(__prop__)) {
          __path__.push(__prop__);
          assert(__obj__.hasOwnProperty(__prop__), 'no ' + __path__.join('.') + ' field');
          assert_eq(__obj__[__prop__], __expected__[__prop__], __addtitional_properties__, __path__);
          __path__.pop();
          __seen__.add(__prop__);
        }
      }
      if(!__addtitional_properties__) {
        for(var __prop__ in __obj__) {
          if(__obj__.hasOwnProperty(__prop__) && !__seen__.has(__prop__)) {
            __path__.push(__prop__);
            assert(false, 'Found unexpected property ' + __path__.join('.'));
          }
        }
      }
    }
    let __checks_global__ = {
      check_1:       function () {
        let __etalon__ = {};
        assert_eq(output, __etalon__, false);
      },
    };
    let __checks_by_test__ = {
      atest : {
        check_2:         function () {
          // [check output] user code begin
assert(output instanceof Object, 'Is not an object!');
          // [check output] user code end
        },
      },
    };
    let __chosen_checks__ = {
      atest : {
        testcase1: ['check_1', 'check_2'],
      },
    };
    let __checks__ =  __chosen_checks__[__test__][__testcase__];
    for(let __check_idx__ in __checks__) {
      let __check_id__ = __checks__[__check_idx__];
      let __checks_bodies_test__ = __checks_by_test__[__test__];
      if(__checks_bodies_test__ && (__check_id__ in __checks_bodies_test__)) {
        (__checks_bodies_test__[__check_id__])();
        continue;
      }
      assert(__check_id__ in __checks_global__, 'check id not found: ' + __check_id__);
      (__checks_global__[__check_id__])();
    }
  }
  __check_output__(__ctx__.__output__, __ctx__.__test__, __ctx__.__testcase__);
  return {__sys__: __ctx__.__sys__};
}
function __get_mocked_resources__(__resources_request__, __test__, __testcase__) {
  function assert(__condition__, __message__) {
    if(!__condition__) {
      throw 'Assertion failed while fetching resource field \'' + __field__ + '\' at testcase ' + __test__ + '.' + __testcase__ + ': ' + __message__;
    }
  }
  const __global_mocks__ = {
    surge_experiment: {
      mock1:       function (resource_request) {
        // [mock body] user code begin
// surge_experiment mock body
        // [mock body] user code end
      },
    },
  };
  const __tests_mocks__ = {
    atest: {
    },
  };
  const __chosen_mocks_by_testcase__ = {
    atest: {
      testcase1: {
        surge_experiment: 'mock1',
      },
    },
  };
  let __result__ = {};
  let __chosen_mocks__ = __chosen_mocks_by_testcase__[__test__][__testcase__];
  for (var __field__ in __resources_request__) {
    let __request__ = __resources_request__[__field__];
    let __mock_id__ = __chosen_mocks__[__request__.name];
    let __test_mocks__ = __tests_mocks__[__test__];
    let __mock_body__;
    if(__request__.name in __test_mocks__ && __mock_id__ in __test_mocks__[__request__.name]) {
      __mock_body__ = __test_mocks__[__request__.name][__mock_id__];
    } else {
      assert(__request__.name in __global_mocks__, 'no mocks for ' + __request__.name);
      assert(__mock_id__ in __global_mocks__[__request__.name], 'mock id not found: ' + __mock_id__);
      __mock_body__ = __global_mocks__[__request__.name][__mock_id__];
    }
    __result__[__field__] = (__mock_body__)(__request__.args);
  }
  return __result__;
}