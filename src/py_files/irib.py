import certifi
import pycurl
import wget


class Storage:
    """
    A class to read channel 3 of Iraninan TV
    """
    def __init__(self):
        self.contents = ''
        self.line = 0

    def store(self, buf):
        self.line = self.line + 1
        self.contents = "%s%i: %s" % (self.contents, self.line, buf)

    def __str__(self):
        return self.contents

def geturl():
    retrieved_body = Storage()
    retrieved_headers = Storage()
    c = pycurl.Curl()
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(c.URL, "https://api.telewebion.com/v2/tv3/live")
    c.setopt(pycurl.HTTPHEADER, ['Connection: keep-alive',
                                 'User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.165',
                                 'Accept: */*',
                                 "Origin: http://tv3.ir",
                                 "Sec-Fetch-Site: cross-site",
                                 "Sec-Fetch-Dest: empty",
                                 "Referer: http://tv3.ir/live",
                                 "Accept-Language: en-US,en;q=0.9"])
    c.setopt(c.WRITEFUNCTION, retrieved_body.store)
    c.setopt(c.HEADERFUNCTION, retrieved_headers.store)
    c.perform()
    c.close()
    for s in retrieved_headers.__str__().split("b'"):
        if s.startswith('Location:'):
            s = s.split()[1].split('\\r')[0]
            data = s.split('?')[0].split('playlist.m3u8')[0]
            filename = wget.download(s)
            f = open(filename, "rt")
            return data + f.read().splitlines()[-1]
