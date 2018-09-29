#! /usr/bin/env python3

import os,sys,cv2
libs='./lib'
sys.path.insert(0,libs)
import smuggler_lib

class camcorder:
    def __init__(self):
        pass
    def record(self,cam=0,qr_dir='camera-captures'):
        if not os.path.exists(qr_dir):
            os.mkdir(qr_dir)
        lib=smuggler_lib.app_qr_handler()

        cap = cv2.VideoCapture(cam)
        while True:
            ret, frame = cap.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

            cv2.imshow('frame', rgb)
            if cv2.waitKey() & 0xFF == ord('q'):
                break 
            if cv2.waitKey() & 0xFF == ord('c'):
                name=os.path.join(qr_dir,lib.mkdefaultName())
                out = cv2.imwrite(name,frame)
                print('{} : captured!'.format(name))


        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app=camcorder()
    app.record()
