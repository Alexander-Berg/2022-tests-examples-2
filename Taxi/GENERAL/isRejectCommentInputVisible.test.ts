import { RejectReason } from 'sections/offers/types';

import { isRejectCommentInputVisible } from './isRejectCommentInputVisible';

describe('isRejectCommentInputVisible', () => {
  it('returns `false` when empty data is provided', () => {
    expect(isRejectCommentInputVisible([], [])).toBe(false);
  });

  it('returns `false` when no `required_reason_message` flag found', () => {
    /* eslint-disable @typescript-eslint/camelcase */
    const reasons: Array<RejectReason> = [
      {
        code: 'reason-1',
        name: 'Reason-1',
        sub_reasons: [
          {
            code: 'reason-2',
            name: 'Reason-2',
            sub_reasons: []
          }
        ]
      },
      {
        code: 'reason-3',
        name: 'Reason-3',
        sub_reasons: []
      }
    ];
    /* eslint-enable @typescript-eslint/camelcase */
    const selectedKeys: Array<string> = [];

    expect(isRejectCommentInputVisible(reasons, selectedKeys)).toBe(false);
  });

  it(
    'returns `false` when reason with `required_reason_message` flag is not selected',
    () => {
    /* eslint-disable @typescript-eslint/camelcase */
      const reasons: Array<RejectReason> = [
        {
          code: 'reason-1',
          name: 'Reason-1',
          sub_reasons: [
            {
              code: 'reason-2',
              name: 'Reason-2',
              sub_reasons: [],
              required_reason_message: true
            }
          ]
        },
        {
          code: 'reason-3',
          name: 'Reason-3',
          sub_reasons: []
        }
      ];
      /* eslint-enable @typescript-eslint/camelcase */
      const selectedKeys: Array<string> = ['reason-1', 'reason-3'];

      expect(isRejectCommentInputVisible(reasons, selectedKeys)).toBe(false);
    }
  );

  it(
    'returns `true` when reason with `required_reason_message` flag is selected',
    () => {
      /* eslint-disable @typescript-eslint/camelcase */
      const reasons: Array<RejectReason> = [
        {
          code: 'reason-1',
          name: 'Reason-1',
          sub_reasons: [
            {
              code: 'reason-2',
              name: 'Reason-2',
              sub_reasons: [],
              required_reason_message: true
            }
          ]
        },
        {
          code: 'reason-3',
          name: 'Reason-3',
          sub_reasons: []
        }
      ];
      /* eslint-enable @typescript-eslint/camelcase */
      const selectedKeys: Array<string> = ['reason-1', 'reason-2'];

      expect(isRejectCommentInputVisible(reasons, selectedKeys)).toBe(true);
    }
  );
});
