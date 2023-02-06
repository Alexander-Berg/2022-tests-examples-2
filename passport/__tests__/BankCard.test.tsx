import React from 'react';

import { BankCard, BankCardPreview } from '..';
import { createClientRender, screen } from '../../../libs/testing';
import { BankCardType, CardBank, CardSystem } from '../constants';

describe('BankCard', () => {
  const render = createClientRender();

  test('should set custom class name', () => {
    render(
      <BankCard
        className="custom-class"
        bankCardType={BankCardType.Default}
        bank={CardBank.Akbars}
        paymentSystem={CardSystem.AmericanExpress}
        cardNumber="4100"
        data-testid="element"
      />,
    );

    expect(screen.getByTestId('element')).toHaveClass('custom-class');
  });

  describe('Snapshots', () => {
    test('Default', () => {
      const result = render(
        <BankCard
          bank={CardBank.ATB}
          paymentSystem={CardSystem.DinersClub}
          bankCardType={BankCardType.Default}
          cardNumber="** 4100"
        />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('WithLabel', () => {
      const result = render(
        <BankCard
          bank={CardBank.ATB}
          paymentSystem={CardSystem.DinersClub}
          bankCardType={BankCardType.Default}
          cardNumber="** 4100"
          label="label"
        />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('WithMoney', () => {
      const result = render(
        <BankCard
          bank={CardBank.ATB}
          paymentSystem={CardSystem.DinersClub}
          bankCardType={BankCardType.Default}
          cardNumber="** 4100"
          money="100 ₽"
        />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('WithLabelMoney', () => {
      const result = render(
        <BankCard
          bank={CardBank.ATB}
          paymentSystem={CardSystem.DinersClub}
          bankCardType={BankCardType.Default}
          cardNumber="** 4100"
          label="label"
          money="100 ₽"
        />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('FamilyOwner', () => {
      const result = render(
        <BankCard
          bank={CardBank.ATB}
          paymentSystem={CardSystem.DinersClub}
          bankCardType={BankCardType.Default}
          label="Семейная"
          cardNumber="** 4100"
        />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('FamilyMember', () => {
      const result = render(
        <BankCard bankCardType={BankCardType.FamilyMember} money="5000 ₽ на неделю" />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('Preview', () => {
      const result = render(
        <BankCardPreview bankCardType={BankCardType.Default} bank={CardBank.Alfa} />,
      );

      expect(result.asFragment()).toMatchSnapshot();
    });

    test('PreviewFamilyMember', () => {
      const result = render(<BankCardPreview bankCardType={BankCardType.FamilyMember} />);

      expect(result.asFragment()).toMatchSnapshot();
    });
  });
});
