import React from "react";
import { shallow } from "enzyme";

import { Router, Routes, Route } from "@yandex-fleet/router";

import UsersRoles from "./UsersRoles";

describe("<UsersRoles />", () => {
  it("renders without crashing", () => {
    const wrapper = shallow(
      <Router>
        <Routes>
          <Route path="user-roles/" element={<UsersRoles />} />
        </Routes>
      </Router>
    );

    expect(wrapper.exists()).toBe(true);
  });
});
