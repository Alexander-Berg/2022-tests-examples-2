import React from "react";
import { shallow } from "enzyme";

import AppShell from "./AppShell";

describe("<AppShell />", () => {
  it("renders without crashing", () => {
    const wrapper = shallow(<AppShell>test</AppShell>);

    expect(wrapper.exists()).toBe(true);
  });
});
