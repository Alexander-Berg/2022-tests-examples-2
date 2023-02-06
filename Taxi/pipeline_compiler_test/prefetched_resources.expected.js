"use strict";
function* __pipeline_perform__(__ctx__) {
  {
    // [logic stage] usage_stage
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.usage_stage = { status: 1 };
    let __stage_meta__ = __stages_meta__.usage_stage;
    try {
      __on_stage_enter__("usage_stage");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let res_alias = __ctx__.__resource__?.preloaded_field;
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