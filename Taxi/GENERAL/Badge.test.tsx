import React from "react";
import { shallow } from "enzyme";

import { Badge } from "./Badge";

describe("Badge", () => {
  it("renders without crashing", () => {
    const wrapper = shallow(<Badge>test</Badge>);

    expect(wrapper.exists()).toBe(true);
  });
});
