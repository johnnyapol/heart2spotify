class CacheManager:
    def __init__(self):
        pass

    def update(self, station, new_songs):
        raise NotImplementedError("Error: Invocation on abstract CacheManager::update")


from pickle import load, dump


class FlatfileCacheManager(CacheManager):
    def __init__(self):
        try:
            with open(".songcache", "rb") as f:
                self.data = load(f)
        except:
            self.data = dict()

    def update(self, station, new_songs):
        if station not in self.data:
            self.data[station] = set()

        diff = new_songs - self.data[station]
        self.data[station] |= diff

        if len(diff) > 0:
            with open(".songcache", "wb") as f:
                dump(self.data, f)

        return diff
