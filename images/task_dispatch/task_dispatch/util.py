def gen_batches(iterable, batch_size=1000):
    batch = []
    for x in iterable:
        batch.append(x)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch
