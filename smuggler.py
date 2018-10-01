#! /usr/bin/env python3
#cmdline util to use smugglerQR
import os,sys
sys.path.insert(0,'./lib')
import argparse
import chunkless,smuggler_lib,handle_one,mkStartEnd,mkgif
import camcorder
class util:
    args={
            'mkcodes':{
                'bytes':{'short':'-b','long':'--bytes','help':'how big of data chunks to contain in each barcode','default':512},
                'mod':{'short':'-m','long':'--mod','help':'how many zeros before the actual integer of the last fname','default':8},
                'fname':{'short':'-f','long':'--fname','help':'input filename','required':'yes'},
                'chunkDir':{'short':'-d','long':'--chunk-dir','help':'where the data chunks are stored','required':'yes'},
                'qrcode-dir':{'short':'-q','long':'--qr-dir','help':'where qrcodes will be stored/placed','required':'yes'},
                'scale':{'short':'-s','long':'--scale-of-code','help':'size of qrcode png image','default':3},
                },
            'assemble':{
                'ofname':{'short':'-f','long':'--fname','help':'output filename','required':'yes'},
                'qrcode-dir':{'short':'-q','long':'--qr-dir','help':'where qrcodes will be stored/placed'},
                'result-dir':{'short':'-r','long':'--result-dir','help':'where the results will be placed','required':'yes'},
                'logfile':{'short':'-j','long':'--json-logfile','help':'where results are stored as a log, or for log based data assembly','required':'yes'},
                'uselog-assemble':{'short':'-l','long':'--assemble-from-log','help':'assemble file using log file','action':'store_true'}
                },
            'getone':{
                'fname':{'short':'-f','long':'--fname','help':'qrcode input fname','required':'yes'},
                'result-dir':{'short':'-r','long':'--result-dir','help':'where resulting log will be appended/created','required':'yes'},
                'logfile':{'short':'-j','long':'--json-logfile','help':'log data to from qrcode','required':'yes'},
                },
            'mkgif':{
                'fname':{'short':'-f','long':'--fname','help':'output gif name','required':'yes'},
                'qrcode-dir':{'short':'-q','long':'--qr-dir','help':'input qrcodes','required':'yes'},
                'result-dir':{'short':'-r','long':'--result-dir','help':'where the resulting gif will be stored','required':'yes'},
                'duration':{'short':'-d','long':'--duration','help':'how long between each frame (seconds)','default':'5'},
                },
            'capture':{
                    'qrcode-dir':{
                    'short':'-q',
                    'long':'--qr-dir',
                    'help':'where qrcodes captured by camera will be stored',
                    'default':'.'},
                'result-dir':{
                    'short':'-r',
                    'long':'--result-dir',
                    'help':'where the resulting log will be stored',
                    'required':'yes'},
                'logfile':{
                    'short':'-j',
                    'long':'--json-logfile',
                    'help':'log data to from qrcode',
                    'required':'yes'},
                'camera':{
                    'short':'-c',
                    'long':'--camera',
                    'help':'camera number default is 0',
                    'default':0},
                'saveFrame':{
                    'short':'-S',
                    'long':'--save-frame',
                    'help':'save qrcode after decoding to qr_dir',
                    'action':'store_true'},
                },
            }
    def __init__(self):
        pass

    def args2dict(self,args):
        return {i:getattr(args,i) for i in dir(args) if not callable(getattr(args,i)) and not i.startswith('__')}
 
    def mkcodes(self,args):
        args=self.args2dict(args)
        if type(args['mod']) == type(str()):
            args['mod']=int(args['mod'])
        if type(args['scale_of_code']) == type(str()):
            args['scale_of_code']=int(args['scale_of_code'])
        if type(args['bytes']) == type(str()):
            args['bytes']=int(args['bytes'])

        if args['scale_of_code'] < 2:
            print('scale of code cannot be below 2! setting scale to minimum!')
            args['scale_of_code']=2

        if args['bytes'] < 256 or args['bytes'] > 512:
            print('bytes is outside of 256-512 range! setting to minum bytes size!')
            args['bytes']=256

        diced=chunkless.sliced()
        diced.dicer(
                args['fname'],
                chunkDir=args['chunk_dir'],
                byteSize=args['bytes']
                )

        f=smuggler_lib.reader()
        
        f.mkcodes(
                args['fname'],
                tmpdir=args['qr_dir'],
                mod=args['mod'],
                scale=args['scale_of_code'],
                chunkDir=args['chunk_dir']
                )
        
        print(args)

    def mkgif(self,args):
        gif=mkgif.mkgif()
        args=self.returnArgsAsDict(args)
        files=[os.path.join(args['result_dir'],'START.png')]
        files.extend([os.path.join(args['qr_dir'],i) for i in os.listdir(args['qr_dir']) if os.path.splitext(i)[1] == '.png'])
        files.append(os.path.join(args['result_dir'],'END.png'))
        caps=True
        for i in [os.path.join(args['result_dir'],'START.png'),os.path.join(args['result_dir'],'END.png')]:
            if not os.path.exists(i):
                caps=False
        if not caps:
            cap=mkStartEnd.mkEnds()
            cap.mkCaps(resultdir=args['result_dir'])
        checked=[i for i in files if os.path.exists(i)] 
        del(files)
        gif.mkgif(fnames=checked,fname=os.path.join(args['result_dir'],args['fname']),duration=int(args['duration']))
        for i in [os.path.join(args['result_dir'],'START.png'),os.path.join(args['result_dir'],'END.png')]:
            os.remove(i)
        print(args)

    def returnArgsAsDict(self,args):
        return {i:getattr(args,i) for i in dir(args) if not callable(getattr(args,i)) and not i.startswith('__')}


    def getone(self,args):
        decoder=handle_one.doOne()
        decoder.store_to_log(args.fname,logfile=args.json_logfile,resultdir=args.result_dir)
        args=self.returnArgsAsDict(args)
        print(args)

    def assemble(self,args):
        args=self.args2dict(args)
        if args['assemble_from_log'] == False and args['qr_dir'] == None:
            exit('at least one of -l or -q must be specified')
        f=smuggler_lib.reader()
        #if type(args['mod']) == type(str()):
        #    args['mod']=int(args['mod'])
        f.readData( 
                useLog=args['assemble_from_log'],
                ofname=args['fname'],
                tmpdir=args['qr_dir'],
                resultdir=args['result_dir'],
                resultJson=args['json_logfile']
            )
        print(args)

    def capture(self,args):
        args=self.returnArgsAsDict(args)
        args['camera']=int(args['camera'])
        if (args['save_frame'] == True) and (args['qr_dir'] == None):
            exit('to use -S, you must specify -q')
        cam=camcorder.camcorder()
        cam.record(
                cam=args['camera'],
                qr_dir=args['qr_dir'],
                result_dir=args['result_dir'],
                logfile=args['json_logfile'],
                saveFrame=args['save_frame'])
        print(args)

    def cmdline(self):
        parser=argparse.ArgumentParser()
        subParsers=parser.add_subparsers()
        parsers={}
        for key in self.args.keys():
            parsers[key]=subParsers.add_parser(name=key)
            for skey in self.args[key].keys():
                op=self.args[key][skey] 
                if skey == 'bytes':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],default=op['default'])
                if skey == 'mod':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],default=op['default'])
                if skey == 'fname':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                if skey == 'chunkDir':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                if skey == 'qrcode-dir':
                    if key == 'mkcodes':
                        parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                    if key == 'assemble':
                        parsers[key].add_argument(op['short'],op['long'],help=op['help'])
                    if key in ['mkgif']:
                        parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                    if key == 'capture':
                        parsers[key].add_argument(op['short'],op['long'],help=op['help'],default=op['default'])
                if skey == 'scale':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],default=op['default'])
                if skey == 'ofname':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                if skey == 'result-dir':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                if skey == 'logfile':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],required=op['required'])
                if skey == 'uselog-assemble':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],action=op['action'])
                if skey == 'duration':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],default=op['default'])
                if skey == 'saveFrame':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],action=op['action'])
                if skey == 'camera':
                    parsers[key].add_argument(op['short'],op['long'],help=op['help'],default=op['default'])
            if key == 'mkcodes':
                parsers[key].set_defaults(func=self.mkcodes)
            elif key == 'assemble':
                parsers[key].set_defaults(func=self.assemble)
            elif key == 'getone':
                parsers[key].set_defaults(func=self.getone)
            elif key == 'mkgif':
                parsers[key].set_defaults(func=self.mkgif)
            elif key == 'capture':
                parsers[key].set_defaults(func=self.capture)
        try:
            options=parser.parse_args()
            options.func(options)
        except:
            exception=sys.exc_info()
            if str(exception[1]) == "'Namespace' object has no attribute 'func'":
                e='No cmd was given!'
            else:
                e=str(exception[1])
            print('\033[1;31;40m{}\033[1;40;m'.format(e))
            options=parser.parse_args('--help'.split())




if __name__ == '__main__':
    a=util()
    a.cmdline()
