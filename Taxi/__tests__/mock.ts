import {ChunkingPeriods} from '../types'

export const mockMaxByDataKeys = {
  cases: [
    {
      chartPoints: [
        {dateString: '2021-07-01', values: {id_graphic: 10, id_graphic2: 330}},
        {dateString: '2021-07-07', values: {id_graphic: 200, id_graphic2: 190}},
        {dateString: '2021-07-07', values: {id_graphic: 200, id_graphic2: 100}},
        {dateString: '2021-07-07', values: {id_graphic: 100, id_graphic2: 150}}
      ],
      dataKeys: [
        {data_key: 'id_graphic', name: 'График1'},
        {data_key: 'id_graphic2', name: 'График2'}
      ],
      stacked: true
    }
  ]
}
export const mockGetPointsLineWithDelta = {
  cases: [
    {
      charts: [
        {
          points_data: [
            {value: 6668, dt_from: '2021-07-27', dt_to: '2021-08-02'},
            {value: 2152, dt_from: '2021-08-03', dt_to: '2021-08-09'},
            {value: 3869, dt_from: '2021-08-10', dt_to: '2021-08-16'},
            {value: 5370, dt_from: '2021-08-17', dt_to: '2021-08-23'},
            {value: 9684, dt_from: '2021-08-24', dt_to: '2021-08-30'},
            {value: 9550, dt_from: '2021-08-31', dt_to: '2021-09-06'},
            {value: 7479, dt_from: '2021-09-07', dt_to: '2021-09-13'}
          ]
        }
      ],
      chunkingPeriod: ChunkingPeriods.DAY,
      result: [
        {x: '2021-07-27', y: 6668},
        {x: '2021-08-03', y: 2152},
        {x: '2021-08-10', y: 3869},
        {x: '2021-08-17', y: 5370},
        {x: '2021-08-24', y: 9684},
        {x: '2021-08-31', y: 9550},
        {x: '2021-09-07', y: 7479}
      ]
    },
    {
      charts: [
        {
          points_data: [
            {value: 8515, dt_from: '2021-07-27', dt_to: '2021-08-02'},
            {value: 5742, dt_from: '2021-08-03', dt_to: '2021-08-09'},
            {value: 9135, dt_from: '2021-08-10', dt_to: '2021-08-16'},
            {value: 5832, dt_from: '2021-08-17', dt_to: '2021-08-23'},
            {value: 4744, dt_from: '2021-08-24', dt_to: '2021-08-30'},
            {value: 7696, dt_from: '2021-08-31', dt_to: '2021-09-06'},
            {value: 4563, dt_from: '2021-09-07', dt_to: '2021-09-13'}
          ]
        }
      ],
      chunkingPeriod: ChunkingPeriods.DAY,
      result: [
        {x: '2021-07-27', y: 8515},
        {x: '2021-08-03', y: 5742},
        {x: '2021-08-10', y: 9135},
        {x: '2021-08-17', y: 5832},
        {x: '2021-08-24', y: 4744},
        {x: '2021-08-31', y: 7696},
        {x: '2021-09-07', y: 4563}
      ]
    }
  ]
}
export const mockFormatPointDateString = {
  cases: [
    {
      date: {dt_from: '2021-07-27', dt_to: '2021-08-02'},
      chunkingPeriod: ChunkingPeriods.DAY
    },
    {
      date: {dt_from: '2021-07-27', dt_to: '2021-08-02'},
      chunkingPeriod: ChunkingPeriods.INTERVAL,
      result: '27.07.21-02.08.21'
    }
  ]
}
export const mockFormatToPoints = {
  cases: [
    {
      charts: [
        {
          points_data: [
            {value: 6668, dt_from: '2021-07-27', dt_to: '2021-08-02'},
            {value: 2152, dt_from: '2021-08-03', dt_to: '2021-08-09'},
            {value: 3869, dt_from: '2021-08-10', dt_to: '2021-08-16'},
            {value: 5370, dt_from: '2021-08-17', dt_to: '2021-08-23'},
            {value: 9684, dt_from: '2021-08-24', dt_to: '2021-08-30'},
            {value: 9550, dt_from: '2021-08-31', dt_to: '2021-09-06'},
            {value: 7479, dt_from: '2021-09-07', dt_to: '2021-09-13'}
          ]
        },
        {
          points_data: [
            {value: 8515, dt_from: '2021-07-27', dt_to: '2021-08-02'},
            {value: 5742, dt_from: '2021-08-03', dt_to: '2021-08-09'},
            {value: 9135, dt_from: '2021-08-10', dt_to: '2021-08-16'},
            {value: 5832, dt_from: '2021-08-17', dt_to: '2021-08-23'},
            {value: 4744, dt_from: '2021-08-24', dt_to: '2021-08-30'},
            {value: 7696, dt_from: '2021-08-31', dt_to: '2021-09-06'},
            {value: 4563, dt_from: '2021-09-07', dt_to: '2021-09-13'}
          ]
        }
      ],
      dataKeys: [
        {data_key: 'id_graphic', name: 'График1'},
        {data_key: 'id_graphic2', name: 'График2'}
      ],
      chunkingPeriod: ChunkingPeriods.DAY,
      result: [
        {dateString: '2021-07-27', values: {id_graphic: 6668, id_graphic2: 8515}},
        {dateString: '2021-08-03', values: {id_graphic: 2152, id_graphic2: 5742}},
        {dateString: '2021-08-10', values: {id_graphic: 3869, id_graphic2: 9135}},
        {dateString: '2021-08-17', values: {id_graphic: 5370, id_graphic2: 5832}},
        {dateString: '2021-08-24', values: {id_graphic: 9684, id_graphic2: 4744}},
        {dateString: '2021-08-31', values: {id_graphic: 9550, id_graphic2: 7696}},
        {dateString: '2021-09-07', values: {id_graphic: 7479, id_graphic2: 4563}}
      ]
    },
    {
      charts: [
        {
          points_data: [
            {value: 8515, dt_from: '2021-07-27', dt_to: '2021-08-02'},
            {value: 5742, dt_from: '2021-08-03', dt_to: '2021-08-09'},
            {value: 9135, dt_from: '2021-08-10', dt_to: '2021-08-16'},
            {value: 5832, dt_from: '2021-08-17', dt_to: '2021-08-23'},
            {value: 4744, dt_from: '2021-08-24', dt_to: '2021-08-30'},
            {value: 7696, dt_from: '2021-08-31', dt_to: '2021-09-06'},
            {value: 4563, dt_from: '2021-09-07', dt_to: '2021-09-13'}
          ]
        }
      ],
      chunkingPeriod: ChunkingPeriods.DAY,
      dataKeys: [{data_key: 'id_graphic', name: 'График1'}],
      result: [
        {dateString: '2021-07-27', values: {id_graphic: 8515}},
        {dateString: '2021-08-03', values: {id_graphic: 5742}},
        {dateString: '2021-08-10', values: {id_graphic: 9135}},
        {dateString: '2021-08-17', values: {id_graphic: 5832}},
        {dateString: '2021-08-24', values: {id_graphic: 4744}},
        {dateString: '2021-08-31', values: {id_graphic: 7696}},
        {dateString: '2021-09-07', values: {id_graphic: 4563}}
      ]
    }
  ]
}
