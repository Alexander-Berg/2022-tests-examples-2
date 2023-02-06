import React from "react";
import { shallow } from "enzyme";

import { Router, Routes, Route } from "@yandex-fleet/router";

import SummaryReportsPage from "./SummaryReports";

describe("<SummaryReportsPage />", () => {
  it("renders without crashing", () => {
    const wrapper = shallow(
      <Router>
        <Routes>
          <Route path="/" element={<SummaryReportsPage />} />
        </Routes>
      </Router>
    );

    expect(wrapper.exists()).toBe(true);
  });
});
