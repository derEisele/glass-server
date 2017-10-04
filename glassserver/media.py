import os
from flask import Response
from glassserver import app
from glassserver import ffmpeg
from glassserver import models

CHUNK_DURATION = 30
BASE_URL = "http://127.0.0.1:1234/"
BANDWIDTHS = ["96000", "21400", "464000"]


@app.route("/hls/<int:file_id>/master.m3u8")
def hls_master(file_id):
    buf = "#EXTM3U\n"
    buf += "#EXT-X-VERSION:3\n"
    for b in BANDWIDTHS:
        buf += "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={}\n".format(b)
        buf += BASE_URL + "hls/{}/master_{}.m3u8\n".format(file_id, b)

    resp = Response(buf, mimetype='application/x-mpegurl')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route("/hls/<int:file_id>/master_<int:bandwidth>.m3u8")
def hls_bandwidth(file_id, bandwidth):

    dbFile = models.MediaFile.query.filter_by(id=file_id).first()
    prefix = dbFile.prefix.path
    path = dbFile.path

    print(prefix)

    ospath = prefix + path
    print(ospath)

    #ospath = "/media/hdd1/TV/shows/Doctor-Who/Doctor-Who_S10E00.mp4"

    max_chunk_duration = 60
    splittimes = ffmpeg.calculate_splittimes(ospath, CHUNK_DURATION)

    buf = '#EXTM3U\n'
    buf += '#EXT-X-VERSION:3\n'
    buf += '#EXT-X-TARGETDURATION:{}\n'.format(CHUNK_DURATION)
    buf += '#EXT-X-MEDIA-SEQUENCE:0\n'

    for (pos, chunk_duration) in splittimes:
        buf += "#EXTINF:{},\n".format(chunk_duration)
        buf += BASE_URL + "frag/{}/{}_{}_{}.ts\n".format(file_id, bandwidth, pos, chunk_duration)

    buf += '#EXT-X-ENDLIST\n'
    resp = Response(buf, mimetype='application/x-mpegurl')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route('/frag/<int:file_id>/<int:bandwidth>_<float:ss>_<float:t>.ts')
def frag(ss, t, bandwidth, file_id):
    #path = os.path.normpath(path)
    #ospath = os.path.join(root_directory, path)

    dbFile = models.MediaFile.query.filter_by(id=file_id).first()
    prefix = dbFile.prefix.path
    path = dbFile.path

    print(prefix)

    ospath = prefix + path
    print(ospath)

    #ospath = "/media/hdd1/TV/shows/Doctor-Who/Doctor-Who_S10E00.mp4"

    data = ffprobe(ospath)
    duration = float(data['format']['duration'])
    # cut at next key frame after given time 'ss'
    _, new_ss = ffmpeg.find_next_keyframe(ospath, ss, t / 2)

    if ss + t * 2 > duration:
        # encode all remain frames at once
        new_t = duration - new_ss
    else:
        # find next key frame after given time 't'
        new_t_prev_duration, new_t = ffmpeg.find_next_keyframe(ospath, ss + t, t / 2)
        new_t -= new_ss
        # minus one frame
        # new_t -= new_t_prev_duration

    process = ffmpeg.stream(ospath, new_ss, new_t, bandwidth)
    resp =  Response(process.stdout, mimetype='video/MP2T')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route("/hls/<int:file_id>.m3u8")
def hls(file_id):

    dbFile = models.MediaFile.query.filter_by(id=file_id).first()
    prefix = dbFile.prefix.path
    path = dbFile.path

    print(prefix)

    ospath = prefix + path
    print(ospath)

    #ospath = "/media/hdd1/TV/shows/Doctor-Who/Doctor-Who_S10E00.mp4"

    #max_chunk_duration = 60
    splittimes = ffmpeg.calculate_splittimes(ospath, CHUNK_DURATION)

    buf = '#EXTM3U\n'
    buf += '#EXT-X-VERSION:3\n'
    buf += '#EXT-X-TARGETDURATION:{}\n'.format(CHUNK_DURATION)
    buf += '#EXT-X-MEDIA-SEQUENCE:0\n'

    for (pos, chunk_duration) in splittimes:
        buf += "#EXTINF:{},\n".format(chunk_duration)
        buf += BASE_URL + "frag/{}/{}_{}.ts\n".format(file_id, pos, chunk_duration)

    buf += '#EXT-X-ENDLIST\n'
    resp = Response(buf, mimetype='application/x-mpegurl')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route('/frag/<int:file_id>/<float:ss>_<float:t>.ts')
def frag(ss, t, file_id):
    #path = os.path.normpath(path)
    #ospath = os.path.join(root_directory, path)

    dbFile = models.MediaFile.query.filter_by(id=file_id).first()
    prefix = dbFile.prefix.path
    path = dbFile.path

    print(prefix)

    ospath = prefix + path
    print(ospath)

    #ospath = "/media/hdd1/TV/shows/Doctor-Who/Doctor-Who_S10E00.mp4"

    data = ffprobe(ospath)
    duration = float(data['format']['duration'])
    # cut at next key frame after given time 'ss'
    _, new_ss = ffmpeg.find_next_keyframe(ospath, ss, t / 2)

    if ss + t * 2 > duration:
        # encode all remain frames at once
        new_t = duration - new_ss
    else:
        # find next key frame after given time 't'
        new_t_prev_duration, new_t = ffmpeg.find_next_keyframe(ospath, ss + t, t / 2)
        new_t -= new_ss
        # minus one frame
        # new_t -= new_t_prev_duration

    process = ffmpeg.stream(ospath, new_ss, new_t)
    resp =  Response(process.stdout, mimetype='video/MP2T')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


def ffprobe(path):
    try:
        data = ffmpeg.ffprobe_data(path)
        if 'format' not in data or \
            'duration' not in data['format']:
            logging.warning('analysis failed for %s: Incomplete data', path)
            return None
        else:
            return data
    except:
        logging.warning('ffprobe failed for %s', path)
    return None


def generateUrls(id):
    urls = {"hls": BASE_URL + "hls/" + str(id) + ".m3u8",
            "mp4": BASE_URL + "mp4/" + str(id) + ".mp4"}
    return urls
