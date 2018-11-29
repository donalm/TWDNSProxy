from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.names import dns
from twisted.names import client, server
from twisted.python import log
import ConfigParser
import sys
import logging

config = ConfigParser.ConfigParser()
config.read('config.ini')


if config.getboolean('twdnsproxy', 'stdout_logging'):
    log.startLogging(sys.stdout)
log.startLogging(open(config.get('twdnsproxy', 'logfile'), 'a'))

def log(line):
    fh = open("/tmp/names.log", "a+")
    fh.write(str(line))
    fh.write("\n")
    fh.close()

class TWDNSProxy(server.DNSServerFactory):
    def gotResolverResponse(self, (ans, auth, add), protocol, message, address):
        log(message.queries[0].name)
        args = (self, (ans, auth, add), protocol, message, address)
        return server.DNSServerFactory.gotResolverResponse(*args)

    def gotResolverError(self, failure, protocol, message, address):
        return server.DNSServerFactory.gotResolverError(self, failure, protocol, message, address)

if __name__ == '__main__':
    csrvs = config.items('Servers')
    srvs = []
    for srvr in csrvs:
        srvs.append((srvr[0], int(srvr[1])))
    resolver = client.Resolver(servers=srvs)
    factory = TWDNSProxy(clients=[resolver], verbose=0)
    protocol = dns.DNSDatagramProtocol(factory)

    reactor.listenUDP(53, protocol)
    reactor.run()
