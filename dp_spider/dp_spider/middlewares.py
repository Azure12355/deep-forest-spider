from twisted.internet.ssl import ClientContextFactory
from twisted.internet._sslverify import ClientTLSOptions


class InsecureContextFactory(ClientContextFactory):
    def getContext(self, hostname=None, port=None):
        ctx = ClientContextFactory.getContext(self)
        ctx.verify_mode = ClientTLSOptions.verify_none
        ctx.check_hostname = False
        return ctx


class InsecureRequestsMiddleware:
    def process_request(self, request, spider):
        if request.meta.get('dont_verify_ssl'):
            request.meta['ssl_context_factory'] = InsecureContextFactory()
