import React from "react";
import { shallow } from "enzyme";

import { SeverityIcon } from ".";

describe("<SeverityIcon />", () => {
  it("renders without crashing", () => {
    const wrapper = shallow(<SeverityIcon severity="critical" />);

    expect(wrapper.exists()).toBe(true);
  });
});
