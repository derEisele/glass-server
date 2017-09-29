import subprocess
import math
from flask import Response

testvideo = "/home/alexander/tmp/test-media/Doctor-Who_S10E06.mp4"
fragLength = 10
fragBase = "http://192.168.100.72:1234/frag"


class StreamBasic(object):
    def __init__(self, path):
        self.path = path

    def stream(self):
        cmdline = "ffmpeg -ss {} -i {} -f {} -vcodec {} -acodec {} -strict experimental -preset ultrafast -movflags frag_keyframe+empty_moov+faststart pipe:1"
        cmdline = cmdline.format(0, self.path, "mp4", "copy", "copy")
        proc = subprocess.Popen(cmdline.split(), stdout=subprocess.PIPE)
        try:
            f = proc.stdout
            byte = f.read(65536)
            while byte:
                yield byte
                byte = f.read(65536)
        finally:
            proc.kill()


class GenerateHLS(object):
    def genPlaylist(self, length):
        n_fragment = math.ceil(length/fragLength)
        pl = """
#EXTM3U
#EXT-X-PLAYLIST-TYPE:VOD
#EXT-X-TARGETDURATION:{fragLength}
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:0
""".format(fragLength=fragLength)

        for i in range(n_fragment):
            pl += """
#EXTINF:10.0,
{file}
""".format(file=fragBase + "/" + str(i) + ".ts")

        pl += "#EXT-X-ENDLIST"

        return pl

    def fragment(path, number):
        start = number * fragLength
        duration = fragLength
        # -bsf h264_mp4toannexb
        cmdline = "ffmpeg -ss {} -t {} -i {} -f {} -vcodec {} -acodec {} pipe:1"
        cmdline = cmdline.format(start, duration, path, "mpegts", "h264", "aac")

        #cmdline = "ffmpeg -ss {} -t {} -i {} -f {} pipe:1"
        #cmdline = cmdline.format(start, duration, path, "mpegts")
        print(cmdline)
        proc = subprocess.Popen(cmdline.split(), stdout=subprocess.PIPE)
        try:
            f = proc.stdout
            byte = f.read(65536)
            while byte:
                yield byte
                byte = f.read(65536)
        finally:
            proc.kill()




def addRoutes(app):

    @app.route("/test")
    def video():
        sb = StreamBasic(testvideo)
        headers = {'Access-Control-Allow-Origin': '*',
                   "Content-Type": "video/mp4",
                   "Content-Disposition": "inline",
                   "Content-Transfer-Enconding": "binary"}
        return Response(response=sb.stream(), headers=headers)

    @app.route("/hls.m3u8")
    def hls():
        length = 48*60 + 44

        headers = {'Access-Control-Allow-Origin': '*',
                   "Content-Type": "vnd.apple.mpegURL"}
        pl = GenerateHLS().genPlaylist(length)

        return Response(response=pl, headers=headers)

    @app.route("/frag/<int:number>.ts")
    def frag(number):
        headers = {'Access-Control-Allow-Origin': '*',
                   "Content-Type": "video/MP2T",
                   "Content-Disposition": "inline",
                   "Content-Transfer-Enconding": "binary"}
        return Response(response=GenerateHLS.fragment(testvideo, number))
