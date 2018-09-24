#! /usr/bin/env python3
#cmdline util to use smugglerQR
import os,sys
sys.path.insert(0,'./lib')
import argparse
import chunkless,smuggler_lib

class util:
    args={
            'mkcodes':{
                'mod':{'short':'-m','long':'--mod','help':'how many zeros before the actual integer of the last fname'},
                'fname':{'short':'-f','long':'--fname','help':'input filename'},
                'chunkDir':{'short':'-d','long':'--chunk-dir','help':'where the data chunks are stored'},
                'qrcode-dir':{'short':'-q','long':'--qr-dir','help':'where qrcodes will be stored/placed'},
                'scale':{'short':'-s','long':'--scale-of-code','help':'size of qrcode png image'},
                },
            'assemble':{
                'mod':{'short':'-m','long':'--mod','help':'how many zeros before the actual integer of the last fname'},
                'ofname':{'short':'-f','long':'--fname','help':'output filename'},
                'qrcode-dir':{'short':'-q','long':'--qr-dir','help':'where qrcodes will be stored/placed'},
                'result-dir':{'short':'-r','long':'--result-dir','help':'where the results will be placed'},
                'logfile':{'short':'-j','long':'--json-logfile','help':'where results are stored as a log, or for log based data assembly'},
                'uselog-assemble':{'short':'-l','long':'--assemble-from-log','help':'assemble file using log file','action':'store_true'}
                }
            }
    def __init__(self):
        pass

    def args2dict(self,args):
        return {i:getattr(args,i) for i in dir(args) if not callable(getattr(args,i)) and not i.startswith('__')}
 
    def mkcodes(self,args):
        args=self.args2dict(args)
        print(args)

    def assemble(self,args):
        args=self.args2dict(args)
        print(args)

    def cmdline(self):
        parser=argparse.ArgumentParser()
        subParsers=parser.add_subparsers()
        parsers={}
        for key in self.args.keys():
            parsers[key]=subParsers.add_parser(name=key)
            for skey in self.args[key].keys():
                if 'action' in self.args[key][skey].keys():
                    op=self.args[key][skey]
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],action=op['action'])
                else:
                    op=self.args[key][skey]
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'])
            if key == 'mkcodes':
                parsers[key].set_defaults(func=self.mkcodes)
            elif key == 'assemble':
                parsers[key].set_defaults(func=self.assemble)
            
        try:
            options=parser.parse_args()
            options.func(options)
        except:
            #print(sys.exc_info())
            options=parser.parse_args('--help'.split())




if __name__ == '__main__':
    a=util()
    a.cmdline()
