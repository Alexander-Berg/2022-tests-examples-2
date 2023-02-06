"use strict";
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
    // [logic stage] stage5
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage5 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage5;
    try {
      __on_stage_enter__("stage5");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let level_1_a = __ctx__.__resource__?.surge_zone?.level_0?.level_1_a;
      let level_2_a = __ctx__.__resource__?.surge_zone?.level_0?.level_1_b?.level_2_a;
      let level_2_b = __ctx__.__resource__?.surge_zone?.level_0?.level_1_b?.level_2_b;
      let level_1_c = __ctx__.__resource__?.surge_zone?.level_0?.level_1_c;
      const __tx_payload__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [logic stage] user code begin

        // [logic stage] user code end
      })();
      if (typeof __tx_payload__ !== 'object') {
        throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
      }
      ++__stage_context__.__iteration_idx__;
      // set status "passed"
      __stage_meta__.status = 0;
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } finally {
      __on_stage_exit__();
    }
  }
  {
    // [logic stage] stage6
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage6 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage6;
    try {
      __on_stage_enter__("stage6");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let level_1_a = __ctx__.__resource__?.surge_zone?.level_0?.level_1_a;
      for (let idx in __ctx__.__resource__?.surge_zone?.level_0?.level_1_b || {}) {
        let __value4__ = __ctx__.__resource__?.surge_zone?.level_0?.level_1_b[idx];
        __stage_context__.idx = idx;
        for (let key in __value4__?.nested_1 || {}) {
          let value = __value4__?.nested_1[key];
          __stage_context__.key = key;
          let aliased = __value4__?.simple_nested;
          const __tx_payload__ = (function(){
            __set_logging_region__("user_code", __stage_context__);
            // [logic stage] user code begin

            // [logic stage] user code end
          })();
          if (typeof __tx_payload__ !== 'object') {
            throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
          }
          ++__stage_context__.__iteration_idx__;
          // set status "passed"
          __stage_meta__.status = 0;
        }
      }
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } finally {
      __on_stage_exit__();
    }
  }
  {
    // [logic stage] old_behaviour
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.old_behaviour = { status: 1 };
    let __stage_meta__ = __stages_meta__.old_behaviour;
    try {
      __on_stage_enter__("old_behaviour");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let szone = __ctx__.__resource__?.surge_zone;
      let renamed = __ctx__.__resource__?.surge_zone?.level_0;
      const __tx_payload__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [logic stage] user code begin

        // [logic stage] user code end
      })();
      if (typeof __tx_payload__ !== 'object') {
        throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
      }
      ++__stage_context__.__iteration_idx__;
      // set status "passed"
      __stage_meta__.status = 0;
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } finally {
      __on_stage_exit__();
    }
  }
  return {__sys__: __ctx__.__sys__};
}