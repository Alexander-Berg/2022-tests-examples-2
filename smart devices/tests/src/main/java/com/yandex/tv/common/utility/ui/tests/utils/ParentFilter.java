package com.yandex.tv.common.utility.ui.tests.utils;

import org.junit.runner.Description;
import org.junit.runner.manipulation.Filter;

public abstract class ParentFilter extends Filter {
  /** {@inheritDoc} */
  @Override
  public boolean shouldRun(Description description) {
    if (description.isTest()) {
      return evaluateTest(description);
    }
    // this is a suite, explicitly check if any children should run
    for (Description each : description.getChildren()) {
      if (shouldRun(each)) {
        return true;
      }
    }
    // no children to run, filter this out
    return false;
  }

  /**
   * Determine if given test description matches filter.
   *
   * @param description the {@link Description} describing the test
   * @return <code>true</code> if matched
   */
  protected abstract boolean evaluateTest(Description description);
}
