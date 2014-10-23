import numpy as np
from flowio.create_fcs import create_fcs


if __name__ == '__main__':
    cluster1 = np.random.multivariate_normal(
        [60000.0, 6000.0, 600.0, 6.0],
        [
            [2000,  100,   10,   10],
            [10,   5000,   10,   10],
            [10,     10, 1000,   10],
            [10,     10,   10,    1]
        ],
        (10000,)
    )
    cluster2 = np.random.multivariate_normal(
        [-100.0, -5.0, 400.0, 4000.0],
        [
            [10,    100,   10,   10],
            [10,      5,   10,   10],
            [1000,   10,   50,   10],
            [10,     10,   10, 5000]
        ],
        (10000,)
    )
    cluster3a = np.random.multivariate_normal(
        [25000, 25000.0, 25000.0, 0],
        [
            [1000,    0,    0,    0],
            [0,    1000,    0,    0],
            [0,       0, 1000,    0],
            [0,       0,    0, 1000]
        ],
        (10000,)
    )
    cluster3b = np.random.multivariate_normal(
        [25000, 0, 25000.0, 25000.0],
        [
            [1000,    0,    0,    0],
            [0,    1000,    0,    0],
            [0,       0, 1000,    0],
            [0,       0,    0, 1000]
        ],
        (10000,)
    )

    data_set1 = np.vstack(
        [
            cluster1,
            cluster2,
            cluster3a
        ]
    ).flatten().tolist()

    data_set2 = np.vstack(
        [
            cluster1,
            cluster2,
            cluster3b
        ]
    ).flatten().tolist()

    channel_names = [
        'channel_A',
        'channel_B',
        'channel_C',
        'channel_D'
    ]

    create_fcs(data_set1, channel_names, 'data_set1.fcs')