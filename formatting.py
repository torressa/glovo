''' Formatting functions'''


def time_to_int(time_to_convert):
    '''Coverts time format to integer'''
    import time
    try:  # for datetime objects
        return int(time.mktime(time_to_convert.timetuple()))
    except:  # for timedelta objects
        return int(time_to_convert.total_seconds())


def previous_and_next(some_iterable):
    '''Gives the previous and next element of any iterable '''
    from itertools import tee, islice, chain, izip
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)
