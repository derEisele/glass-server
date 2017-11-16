import os
from flask import Response
from flask import jsonify
from flask import request
from flask import render_template
from glassserver import app
from glassserver import ffmpeg
from glassserver import models
from glassserver import infocollecter
from glassserver import mediacache

CHUNK_DURATION = 30
#BASE_URL = "https://192.168.100.10:444/api/"
#BASE_URL = "http://192.168.100.10:1234/api/"
BANDWIDTHS = [800, 1440, 2300, 3000, 4000, 8000]
AR = 16/9


def baseURL():
    return request.url_root + "api/"


@app.route("/glass/test")
def glass():
    return "glass/test"

@app.route("/test")
def root():
    return "test"

@app.route("/api/hls/<int:file_id>/master.m3u8")
def hls_master(file_id):
    buf = "#EXTM3U\n"
    buf += "#EXT-X-VERSION:3\n"
    for b in BANDWIDTHS:
        r = ffmpeg.resolutionMap(b)
        buf += "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={},RESOLUTION={}x{}\n".format(b, r[0], r[1])
        buf += baseURL() + "hls/{}/index_{}.m3u8\n".format(file_id, b)

    resp = Response(buf, mimetype='application/x-mpegurl')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route("/api/hls/<int:file_id>/index_<int:bandwidth>.m3u8")
def hls_bandwidth(file_id, bandwidth):

    dbFile = models.MediaFile.query.filter_by(id=file_id).first()
    prefix = dbFile.prefix.path
    path = dbFile.path

    print(prefix)

    ospath = prefix + path
    print(ospath)

    #ospath = "/media/hdd1/TV/shows/Doctor-Who/Doctor-Who_S10E00.mp4"

    max_chunk_duration = 60
    #splittimes = ffmpeg.calculate_splittimes(ospath, CHUNK_DURATION)
    splittimes = mediacache.calc_splittimes(ospath, CHUNK_DURATION)

    buf = '#EXTM3U\n'
    buf += '#EXT-X-VERSION:3\n'
    buf += '#EXT-X-TARGETDURATION:{}\n'.format(CHUNK_DURATION)
    buf += '#EXT-X-MEDIA-SEQUENCE:0\n'

    for (pos, chunk_duration) in splittimes:
        buf += "#EXTINF:{},\n".format(chunk_duration)
        buf += baseURL() + "frag/{}/{}_{}_{}.ts\n".format(file_id, bandwidth, pos, chunk_duration)

    buf += '#EXT-X-ENDLIST\n'
    resp = Response(buf, mimetype='application/x-mpegurl')
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route('/api/dash/<int:file_id>/manifest.mpd')
def dash_manifest(file_id):
    representations = [{"id": 1, "bandwidth": 800, "height": 720, "width": 1280},
                       {"id": 2, "bandwidth": 2000, "height": 1080, "width": 1920}]

    resp = render_template("manifest.mpd",
                           duration="42S",
                           representations=representations)

    return Response(resp, mimetype="application/octet-stream")


@app.route('/api/frag/<int:file_id>/<int:bandwidth>_<float:ss>_<float:t>.ts')
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
    #_, new_ss = ffmpeg.find_next_keyframe(ospath, ss, t / 2)
    new_ss = ss
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

    #  VERY, VERY IMPORTANT TO AVOID MEMORY OVERFLOW!!!!!!!
    process.kill
    del process
    resp.headers.extend({"Access-Control-Allow-Origin": "*",
                         "Access-Control-Expose-Headers": "Content-Length"})
    return resp


@app.route("/api/importAll")
def importAll():
    infocollecter.importAll()
    return jsonify({"Info": "Started import"})


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
        print('ffprobe failed for %s', path)
    return None


def generateUrls(id):
    urls = {"hls": baseURL() + "hls/" + str(id) + "/master.m3u8"}
            #"mp4": BASE_URL + "mp4/" + str(id) + ".mp4"}
    return urls
