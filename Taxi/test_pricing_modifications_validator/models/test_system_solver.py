import pytest

import pricing_modifications_validator.models.numeric.solver as solver
import pricing_modifications_validator.models.numeric.systems as systems


@pytest.mark.parametrize(
    'eq_data,var_data,result,comment',
    [
        (
            ['x[0] + x[1] - 2', 'x[0]*x[1]-1', 'x[0]-x[1]'],
            ['x', 'y'],
            True,
            'simple',
        ),
        (
            [
                '-3*x[0] - 3*x[1] - 3*x[2] + 18',
                '-4*x[0] - 6*x[1] - x[2] + 18',
                '3*x[0] + 5*x[1] - 3*x[2] + 18',
            ],
            ['A', 'B', 'C'],
            True,
            'linear system',
        ),
        (
            ['x[0]-5-x[2]*x[2]', 'x[1]-5-x[3]*x[3]', '10-x[0]-x[1]-x[4]*x[4]'],
            ['x', 'y', '', '', ''],
            True,
            'x >= 5, y>= 5, x + y <= 10',
        ),
        (
            ['x[0]-4-x[2]*x[2]', 'x[1]-4-x[3]*x[3]', '10-x[0]-x[1]-x[4]*x[4]'],
            ['x', 'y', '', '', ''],
            True,
            'x >= 4, y>= 4, x + y <= 10',
        ),
        (
            [
                'x[2]*x[2]*(1-x[0]*x[0]-x[1]*x[1])-1',
                'x[3]*x[3]*(x[0]+x[1]-1.3)-1',
            ],
            ['x', 'y', '', ''],
            True,
            'x*x +y*y < 1, x+y > 1.3',
        ),
        (
            ['1-x[0]*x[0]-x[1]*x[1]', 'x[0]+x[1]-1', 'x[2]*(x[0]-1) - 1'],
            ['x', 'y', ''],
            True,
            'x*x +y*y  == 1, x+y =1, x != 1',
        ),
        (
            ['cos(x[0]) - x[1] - x[2]*x[2]', 'x[1]-x[0]*x[0] -1 - x[3]*x[3]'],
            ['x', 'y', '', ''],
            True,
            'y <= cos(x), y >= x*x - 1',
        ),
        (
            ['cos(x[1])', 'x[0]*x[0] + x[1]*x[1] - 25'],
            ['x', 'y'],
            True,
            ' x^2 + y^2 = 25, cos y = 0',
        ),
        (
            [
                'x[2]*x[2]*(sin(x[0])-x[1])-1',
                'x[3]*x[3]*(x[1]-cos(x[0])-1.41) - 1',
            ],
            ['x', 'y', '', ''],
            True,
            'y < sin(x)  y > cos(x) + 1.41',
        ),
        (
            [
                'x[2]*x[2]*(sin(x[0])-x[1])-1',
                'x[3]*x[3]*(x[1]-cos(x[0])-1.48) - 1',
            ],
            ['x', 'y', '', ''],
            False,
            'y < sin(x)  y > cos(x) + 1.48',
        ),
        (
            [
                'x[2]*x[2]*(x[0] +x[1]) - 1',
                'x[3]*x[3]*(x[0] - x[1]) - 1',
                'x[4]*x[4]*x[0] + 1',
            ],
            ['x', 'y', '', '', ''],
            False,
            'x+y > 0, x - y > 0, x < 0',
        ),
    ],
)
def test_system_solver(eq_data, var_data, result, comment):
    system_data = systems.SystemData(eq_data, var_data)
    point, iterations = solver.solve(system_data)
    assert iterations is not None
    assert (point is not None) is result
