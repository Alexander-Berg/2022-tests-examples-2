import React from "react";
import { mount } from "enzyme";

import { I18nextProvider } from "@yandex-fleet/i18n";
import i18nMock from "@yandex-fleet/i18n/src/i18nMock";

import { Table, LinkCell, LinkCellProps } from "../..";

describe("LinkCell", () => {
  it("renders without crashing", () => {
    type Data = {
      id: string;
    };

    const data = [{ id: "1" }, { id: "2" }];

    const IdCell = (props: LinkCellProps<Data>) => {
      const href = `/#${props.cell.value}`;

      return <LinkCell {...props} href={href} />;
    };

    const columns = [
      {
        Header: "id",
        accessor: (item: Data) => item.id,
        Cell: IdCell,
      },
    ];

    const wrapper = mount(
      <I18nextProvider i18n={i18nMock}>
        <Table columns={columns} data={data} />
      </I18nextProvider>
    );

    expect(wrapper.find(IdCell)).toHaveLength(2);
  });
});
