"use strict";

// user global code
function foo() { return 'bar'; }
// end user global code

function* __pipeline_perform__(__ctx__) {
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
    // [logic stage] stage1
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage1 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage1;
    try {
      __on_stage_enter__("stage1");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      for (let class_name in __ctx__.__resource__?.surge_experiment?.rules || {}) {
        let rule = __ctx__.__resource__?.surge_experiment?.rules[class_name];
        __stage_context__.class_name = class_name;
        // [in binding] access value
        let base_class = __ctx__.__resource__?.surge_zone?.base_class;
        // [in binding] access value
        let some_item0 = __ctx__.__resource__?.surge_zone?.some_array?.[0];
        // [in binding] access value
        let some_item11 = __ctx__.__resource__?.surge_zone?.some_array?.[11];
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
  return {__sys__: __ctx__.__sys__};
}