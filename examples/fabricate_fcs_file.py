import numpy as np
from flowio.create_fcs import create_fcs


if __name__ == '__main__':
    # these clusters have lots of overlap
    # cluster1 = np.random.multivariate_normal(
    #     [60000.0, 6000.0, 600.0, 6.0],
    #     [
    #         [2000,  100,   10,   10],
    #         [10,   5000,   10,   10],
    #         [10,     10, 1000,   10],
    #         [10,     10,   10,    1]
    #     ],
    #     (10000,)
    # )
    # cluster2 = np.random.multivariate_normal(
    #     [-100.0, -5.0, 400.0, 4000.0],
    #     [
    #         [10,    100,   10,   10],
    #         [10,      5,   10,   10],
    #         [1000,   10,   50,   10],
    #         [10,     10,   10, 5000]
    #     ],
    #     (10000,)
    # )
    # cluster3a = np.random.multivariate_normal(
    #     [25000, 25000.0, 25000.0, 0],
    #     [
    #         [1000,    0,    0,    0],
    #         [0,    1000,    0,    0],
    #         [0,       0, 1000,    0],
    #         [0,       0,    0, 1000]
    #     ],
    #     (10000,)
    # )
    # cluster3b = np.random.multivariate_normal(
    #     [25000, 0, 25000.0, 25000.0],
    #     [
    #         [1000,    0,    0,    0],
    #         [0,    1000,    0,    0],
    #         [0,       0, 1000,    0],
    #         [0,       0,    0, 1000]
    #     ],
    #     (10000,)
    # )

    # these clusters are clearly separated
    cluster1 = np.random.multivariate_normal(
        [6000.0, 6000.0, 0.0, 3000.0],
        [
            [600000,  600000,   0,   0],
            [300000,   1,   0,   0],
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

    create_fcs(data_set1, channel_names, 'data_set1.fcs')
    create_fcs(data_set2, channel_names, 'data_set2.fcs')