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
      __fetch_resources__(__fetch_args__);
    } finally {
      __on_stage_exit__();
    }
  }
  // Intentionally do not store in __ctx__
  let __predicate_predicate_stage__ = null;
  {
    // [predicate stage] predicate_stage
    {
      let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
      // set status "omitted" by default
      __stages_meta__.predicate_stage = { status: 1 };
      let __stage_meta__ = __stages_meta__.predicate_stage;
      // [in binding] access value
      let base_class = __ctx__.__resource__?.surge_zone?.base_class;
      __predicate_predicate_stage__ = function(__stage_context__, argument){
        __set_logging_region__("predicate_predicate_stage", __stage_context__);
        // [predicate stage] user code begin
return true;
        // [predicate stage] user code end
      };
    }
  }
  {
    // [logic stage] call_predicate
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.call_predicate = { status: 1 };
    let __stage_meta__ = __stages_meta__.call_predicate;
    try {
      __on_stage_enter__("call_predicate");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let some_value = __ctx__.__input__?.some_value;
      if (!__predicate_predicate_stage__(__stage_context__, some_value)) {
        const __tx_payload__ = (function(){
          __set_logging_region__("user_code", __stage_context__);
          // [logic stage] user code begin
return {value_raw: some_value + 1};
          // [logic stage] user code end
        })();
        if (typeof __tx_payload__ !== 'object') {
          throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
        }
        if (__tx_payload__ !== null) {
          __set_logging_region__("out_bindings", __stage_context__);
          let stage_outs = new Set(['value_raw']);
          for (let alias in __tx_payload__) {
            if (!stage_outs.has(alias)) {
              throw 'no out named "' + alias + '"';
            }
          }
          if (stage_outs.length > Object.keys(__tx_payload__).length) {
             throw 'expected more outputs than provided';
          }
          (function (__root_object__, __value_to_set__) {
            // [out binding] access value
            // [out binding] assignment
            __root_object__.value_raw = __value_to_set__;
            return;
          })(__ctx__.__output__.__trx__, __tx_payload__['value_raw']);
        }
        ++__stage_context__.__iteration_idx__;
        // set status "passed"
        __stage_meta__.status = 0;
      }
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } catch (error) {
      log.error("Stage failed: " + error);
      // set status "failed"
      __stage_meta__.status = 2;
      __stage_meta__.error = error;
      // set proper error type for stats
      __stage_meta__.error_type = error.__ytx_custom_error_type__ || null;
      // reset changes in output bindings
      __ctx__.__output__.__rollback__();
    } finally {
      __on_stage_exit__();
    }
  }
  return {__sys__: __ctx__.__sys__};
}