from glassserver import ffmpeg

SPLITTIMES = dict()


def calc_splittimes(ospath, chunk_duration):
    global SPLITTIMES
    if len(SPLITTIMES) > 20:
        SPLITTIMES = dict()
    if ospath in SPLITTIMES:
        print("---------------------------LOADED SPLITTIMES FROM CACHE------------")
        return SPLITTIMES[ospath]
    else:
        print("---------------------------GENERATED SPLITTIMES--------------------")
        splittimes = tuple(ffmpeg.calculate_splittimes(ospath, chunk_duration))
        SPLITTIMES[ospath] = splittimes
        return SPLITTIMES[ospath]
