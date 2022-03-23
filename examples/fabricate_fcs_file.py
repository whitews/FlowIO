import numpy as np
from flowio.create_fcs import create_fcs


if __name__ == '__main__':
    np.random.seed(42)

    # these clusters are clearly separated
    cluster1 = np.random.multivariate_normal(
        [6000.0, 6000.0, 0.0, 3000.0],
        [
            [600000,  300,   0,   0],
            [300,   1000,   0,   0],
            [0,     0, 1,   10],
            [0,     0,   10,    1000]
        ],
        (2000,)
    )
    cluster2 = np.random.multivariate_normal(
        [-10.0, 0.0, 0.0, 0.0],
        [
            [10000,    100,   0,   0],
            [100,      10000,   0,   0],
            [0,   0,   100000,   0],
            [0,     0,   0, 1000]
        ],
        (2000,)
    )
    cluster3a = np.random.multivariate_normal(
        [7000.0, 2000.0, -6.0, 1500],
        [
            [100000,    100,    0,    0],
            [100,    100000,    100,    0],
            [0,       100, 10000,    0],
            [0,       0,    0, 10000]
        ],
        (2000,)
    )
    cluster3b = np.random.multivariate_normal(
        [2000.0, 7000.0, 1500.0, -6.0],
        [
            [100000,    100,    0,    0],
            [100,    100000,    100,    0],
            [0,       100, 10000,    0],
            [0,       0,    0, 10000]
        ],
        (2000,)
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

    fh = open('data_set1.fcs', 'wb')
    create_fcs(fh, data_set1, channel_names)
    fh.close()

    fh = open('data_set2.fcs', 'wb')
    create_fcs(fh, data_set2, channel_names)
    fh.close()
