import pandas as pd
import numpy as np
from fxdayu_data.data.decorators import value_wrapper


def exhaust(iterable, *iters):
    if len(iters):
        for i in iterable:
            for e in exhaust(*iters):
                e.insert(0, i)
                yield e
    else:
        for i in iterable:
            yield [i]


def match(iterable, *iters):
    for ex in map(exhaust, iterable, *iters):
        for e in ex:
            yield e


def multi_from_frame(frame):
    names = []
    items = []
    for name, item in frame.iteritems():
        names.append(name)
        items.append(item.values)

    return pd.MultiIndex.from_arrays(items, names=names)


multi_exhaust = value_wrapper(list, pd.MultiIndex.from_tuples)(exhaust)
multi_match = value_wrapper(list, pd.MultiIndex.from_tuples)(match)


def frame_2_multi_series(frame, names=None):
    if isinstance(frame, pd.DataFrame):
        value = np.concatenate(frame.values)
        index = multi_exhaust(frame.index, frame.columns)
        if names:
            index = index.set_names(names)
        return pd.Series(value, index)

    else:
        raise TypeError('type of frame should be pandas.DataFrame')


def tsf_2_multi_frame(time_frame, columns=None, names=None):
    first = []
    second = []
    values = []
    for time, frame in time_frame:
        if isinstance(frame, pd.DataFrame):
            first.append([time])
            second.append(frame.index)
            values.append(frame.values)
        else:
            raise TypeError('type of frame in time_frame should be pandas.DataFrame')

    index = multi_match(first, second)
    if names:
        index = index.set_names(names)
    frame = np.concatenate(values)
    return pd.DataFrame(frame, index, columns)


def make_multi_frame(data, **kwargs):
    results = {name: np.concatenate(func(data).values) for name, func in kwargs.items()}
    index = multi_exhaust(data.index, data.columns)
    return pd.DataFrame(
        results, index
    )


if __name__ == '__main__':
    from fxdayu_data.data import MongoHandler
    from datetime import datetime

    mh = MongoHandler(db='HS')
    pl = mh.read(['000001.D', '600000.D'], start=datetime(2016, 1, 1))
    close = frame_2_multi_series(pl.minor_xs('close'), ['datetime', 'code'])
    pd.Series()