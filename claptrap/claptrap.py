#! /usr/bin/env python3
#NoGuiLinux

import json,random,os,base64,argparse,shutil,stat
try:
    from Cryptodome.Cipher import AES
except:
    from Crypto.Cipher import AES

class Zero:
    def __init__(self):
        pass

    def encrypt(self,chunk,key,num,msg):
        cipher=AES.new(key,AES.MODE_EAX)
        nonce=cipher.nonce
        ciphertext,tag=cipher.encrypt_and_digest(chunk)
        #nonce,tag,len(ciphertext),data
        print(msg,'nonce: {}'.format(len(nonce)),'dataLen: {}'.format(len(ciphertext)),'tag: {}'.format(len(tag)),'chunk: {}'.format(num))
        return nonce,tag,len(ciphertext),key,ciphertext

    def jsonHandlerE_chunk(self,dataTuple):
        export={
                    'key':'',
                    'nonce':'',
                    'tag':'',
                    'len':0,
                }
        if len(dataTuple) == 5:
            export['key']=base64.b64encode(dataTuple[3]).decode()
            export['nonce']=base64.b64encode(dataTuple[0]).decode()
            export['tag']=base64.b64encode(dataTuple[1]).decode()
            export['len']=dataTuple[2]
        return export

    def randomKey(self):
        return os.urandom(32)

    def simpleRunE(self,key,datafile,eDatafile,keyfile,eKeyfile):
        if self.exists(datafile) == None:
            return None
        keyseg={}
        data={}
        num=0
        with open(eDatafile,'wb') as df:
            with open(datafile,'rb') as pt:
                while True:
                    msg=pt.read(random.randint(8,1024))
                    if not msg:
                        break
                    #for num,i in enumerate(msg):
                    data=self.encrypt(msg,self.randomKey(),num,'{} -> {}'.format(datafile,eDatafile))
                    keyseg[str(num)]=self.jsonHandlerE_chunk(data)
                    df.write(data[-1])
                    num+=1
        
        with open(keyfile,'w') as kf:
            json.dump(keyseg,kf) 

        self.encrypt_key(key,keyfile,eKeyfile)
        os.remove(datafile)
        return True

    def encrypt_key(self,key,keyfile,eKeyfile):
        num=0
        with open(eKeyfile,'wb') as ekf:
            with open(keyfile,'rb') as kf:
                while True:
                    d=kf.read(128)
                    if not d:
                        break
                    res=self.encrypt(d,key,num,'{} -> {}'.format(keyfile,eKeyfile))
                    ctext=res[0]+res[-1]+res[1]
                    print('ctext: {}'.format(len(ctext)),'nonce {}'.format(len(res[0])),'data {}'.format(len(res[-1])),'tag {}'.format(len(res[1])))
                    ekf.write(ctext)
                    num+=1
        os.remove(keyfile)

    def decrypt_key(self,key,keyfile,eKeyfile):
        count=0
        with open(eKeyfile,'rb') as ekf, open(keyfile,'wb') as kf2:
            while True:
                d=ekf.read(16+128+16)
                if not d:
                    break
                com={}
                com['nonce']=base64.b64encode(d[:16]).decode()
                if len(d) != (16+128+16):
                    chunk=d[16:len(d)-16]
                else:
                    chunk=d[16:128+16]
                com['tag']=base64.b64encode(d[128+16:]).decode()
                com['key']=base64.b64encode(key).decode()
                res=self.decrypt(chunk,com,'{} -> {} : chunk {}'.format(eKeyfile,keyfile,count))
                kf2.write(res)
                count+=1
        os.remove(eKeyfile)

    def exists(self,name):
        if not os.path.exists(name):
            print('{} : does not exist'.format(name))
            return None
        elif not os.path.isfile(name):
            print('{} : not a file'.format(name))
            return None
        else:
            return True

    def simpleRunD(self,key,datafile,eDatafile,keyfile,eKeyfile):        
        if self.exists(eDatafile) == None:
            return None

        self.decrypt_key(key,keyfile,eKeyfile)
        keyseg={}

        with open(datafile,'wb') as pt:
            with open(keyfile,'r') as kf:
                keyseg=json.load(kf)
            with open(eDatafile,'rb') as df:
                for i in keyseg.keys():
                    chunk=df.read(int(keyseg[i]['len']))
                    res=self.decrypt(chunk,keyseg[i],'{} -> {} : chunk {}'.format(eDatafile,datafile,i))
                    pt.write(res)
        for i in [keyfile,eDatafile]:
            os.remove(i)

        return True
        
    def decrypt(self,chunk,dataDict,msg):
        nonce=base64.b64decode(dataDict['nonce'])
        tag=base64.b64decode(dataDict['tag'])
        key=base64.b64decode(dataDict['key'])
        cipher=AES.new(key,mode=AES.MODE_EAX,nonce=nonce)
        plaintext=cipher.decrypt(chunk)
        try:
            cipher.verify(tag)
            print('all good!',msg)
        except ValueError:
            print('chunk may be corrupted, or compromised!',msg)
        return plaintext
    def fixKey(self,key):
        try:
            if type(key) == type(str()):
                key=key.encode()
            if len(key) < 32:
                key=key+b' '*(32-len(key))
            elif len(key) > 32:
                print('warning: key is longer than supported (32 chars)... truncating to 32')
                key=key[:32]
            return key
        except:
            print('ERROR! "{}"'.format(key))
            return None

class Roland:
    #cmdline utility class
    #if claptrap.py is not imported as a module
    modes=['enc','dec']
    tmpdir='.tmp'
    def __init__(self):
        self.tmpdir=os.path.join(os.environ['HOME'],self.tmpdir)

    def cmdline(self):
        parser=argparse.ArgumentParser()
        args={
                'datafile':{'short':'-d','long':'--datafile','help':'unencrypted data file','req':'yes'},
                'edatafile':{'short':'-e','long':'--eDatafile','help':'encrypted data file','req':'yes'},
                'keyfile':{'short':'-k','long':'--keyfile','help':'file containing keys to eDatafile','req':'yes'},
                'password':{'short':'-p','long':'--password','help':'passwork to lock keyfile','req':'yes'},
                'mode':{'short':'-m','long':'--mode','help':'dec or enc','req':'yes'},
                }
        for key in args.keys():
                parser.add_argument(args[key]['short'],args[key]['long'],help=args[key]['help'],required=args[key]['req'])

        options=parser.parse_args()
        return options

    def mkkeynames(self,keyfile,mode):
        kf=os.path.join(self.tmpdir,os.path.basename(keyfile)+'_tmp.json')
        ekf=os.path.join(self.tmpdir,os.path.basename(keyfile)+'_tmp.eJson')
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
        os.mkdir(self.tmpdir)
        if mode == 'dec':
            if not os.path.exists(keyfile):
                print('keyfile does not exist')
                return None
            
            if not os.path.isfile(keyfile):
                print('keyfile is not a file')
                return None

            with open(keyfile,'rb') as kfp, open(ekf,'wb') as ekfp:
                while True:
                    d=kfp.read(512)
                    if not d:
                        break
                    ekfp.write(d)
            return kf,ekf
        elif mode == 'enc':
            return kf,keyfile

    def permissions_read(self,name):
        d=os.path.dirname(name)
        if d == '':
            d='.'
        if not os.path.exists(d):
            return False,'{} : does not exist!'.format(d)

        uid=os.getuid()
        if uid == 0:
            return True,''
        gid=os.getgid()

        st=os.stat(d)
        if uid == st.st_uid:
            status=bool(st.st_mode & stat.S_IRUSR)
        else:
            status=False
        if status == False:
            status=bool(st.st_mode & stat.S_IRGRP)
        if status == False:
            status=bool(st.st_mode & stat.S_IROTH)
        return status,''

    def permissions_write(self,name):
        d=os.path.dirname(name)
        if d == '':
            d='.'
        if not os.path.exists(d):
            return False,'{} : does not exist!'.format(d)
        uid=os.getuid()
        if uid == 0:
            return True,''
        gid=os.getgid()

        st=os.stat(d)
        if uid == st.st_uid:
            status=bool(st.st_mode & stat.S_IWUSR)
        else:
            status=False
        if status == False:
            status=bool(st.st_mode & stat.S_IWGRP)
        if status == False:
            status=bool(st.st_mode & stat.S_IWOTH)
        return status,''

    def ops(self):
        zero=Zero()
        options=self.cmdline()
        if options.mode in self.modes:
            options.datafile=os.path.expanduser(options.datafile)
            options.eDatafile=os.path.expanduser(options.eDatafile)
            options.keyfile=os.path.expanduser(options.keyfile)
            #check to see if user can read/write to locations above
            checks=[
                        [options.keyfile,self.permissions_read],
                        [options.keyfile,self.permissions_write],
                        [options.datafile,self.permissions_read],
                        [options.datafile,self.permissions_write],
                        [options.eDatafile,self.permissions_read],
                        [options.eDatafile,self.permissions_write],
                    ]
            for name,call in checks:
                result=call(name)
                if result[0] == False:
                    if result[1] == '':
                        print('permissions might not permit operation! aborting! {} : {}'.format(name,result[0]))
                    else:
                        print(result[1])
                    return None

            if options.mode == 'enc':
                ks=self.mkkeynames(options.keyfile,'enc')
                keyfile=ks[0]
                eKeyfile=ks[1]
                key=zero.fixKey(options.password)
                if key != None:
                    stat=zero.simpleRunE(key,options.datafile,options.eDatafile,keyfile,eKeyfile)
            elif options.mode == 'dec':
                ks=self.mkkeynames(options.keyfile,'dec')
                if ks != None:
                    keyfile=ks[0]
                    eKeyfile=ks[1]
                    key=zero.fixKey(options.password)
                    if key != None:
                        stat=zero.simpleRunD(key,options.datafile,options.eDatafile,keyfile,eKeyfile)
                        if stat == True:
                            try:
                                os.remove(options.keyfile)
                            except OSError as err:
                                print('whoopsie! looks like you can\'t delete the keyfile!\n',err)
            shutil.rmtree(self.tmpdir)
        else:
            print('use "dec" or "enc"!')

if __name__ == '__main__':
    commander=Roland()
    commander.ops()
