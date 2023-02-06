import React from 'react';

import i18n from '../../../../services/i18n';

type StatusProps = {
  value: boolean;
}

export default function Status({
  value,
}: StatusProps) {
  return (
    <div style={{
      textAlign: 'center',
      width: '100px',
      padding: '5px 0',
      borderRadius: '4px',
      backgroundColor: value ? '#D8FFDC' : '#FFD8D8',
      boxShadow: '0 2px 2px 1px rgba(0,0,0,0.05)'
    }}>
      { value ? i18n.t("PAGE_TESTING.MATCHED") : i18n.t("PAGE_TESTING.NOT_MATCHED") }
    </div>
  )
}
