# coding:utf-8
import ConfigParser
import json
import os
import subprocess
import sys
import urllib
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

"""
this py aim to run a hook server ,when git repo push sth ,it will do hexo deploy
"""
cp = ConfigParser.SafeConfigParser()
cp.read('webhook.conf')

hexo_repo_dir = cp.get("webhookconf", "hexo_repo_dir")
hexo_repo_post_dir = os.path.join(hexo_repo_dir, cp.get("webhookconf", "hexo_content_name"))


class RequestHandler(BaseHTTPRequestHandler):
    def _writeheaders(self):
        self.send_response(200);
        self.send_header('Content-type', 'application/json');
        self.end_headers()

    def do_Head(self):
        self.send_error(400)
        # self._writeheaders()

    def do_GET(self):
        self.send_error(400)
        # self._writeheaders()
        # self.wfile.write(str(self.headers))

    def do_POST(self):
        try:
            print "path: %s" % self.path
            print "heads: \r\n%s" % self.headers
            if self.path[1:] != cp.get("webhookconf", "path"):
                self.send_error(404)
                return
            self._writeheaders()
            length = self.headers.getheader('content-length');
            nbytes = int(length)
            data = self.rfile.read(nbytes)
            # print data
            data = urllib.unquote(data)
            print "payload: %s" % data
            json_obj = json.loads(data)
            if json_obj.get("event") == cp.get("webhookconf", "event") and json_obj.get("ref") == cp.get("webhookconf",
                                                                                                         "branch"):
                # git pull
                git_pull_cmd = "PATH=$PATH:/usr/local/bin && PATH=$PATH:/usr/bin && pwd && git pull"
                git_pull_result = subprocess.check_output([git_pull_cmd], shell=True, cwd=hexo_repo_dir)
                print git_pull_result
                self.wfile.write(git_pull_result)
                # if push to master
                hexo_deployer_sh_path = os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0],
                                                     "hexo_deployer.sh")
                delpoyer_result = subprocess.check_output(
                    [("chmod 777 %s && sh %s" % (hexo_deployer_sh_path, hexo_deployer_sh_path))],
                    shell=True,
                    cwd=hexo_repo_post_dir)
                print delpoyer_result
                self.wfile.write(delpoyer_result)
            self.wfile.write(data)
        except Exception, e:
            print e
            self.send_error(503)


if __name__ == "__main__":
    addr = ('', int(cp.get("webhookconf", "port")))
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
