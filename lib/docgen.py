#! /usr/bin/env python3
import os,sys
from reportlab.lib.enums import *
from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
#SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import *
import reportlab.lib.styles
from reportlab.lib.units import inch
from reportlab.lib.colors import *
#set fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class styles:
    def __init__(self):
        self.mkDefaultTableStyleCenter()
    
    def mkDefaultTableStyleCenter(self):
            self.defaultTableCenter=TableStyle(
                    [
                        ('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('VALIGN',(0,0),(-1,-1),'TOP'),
                        ('LINEBELOW',(0,0),(-1,-1),1.5,red),
                        ('LINEBEFORE',(0,0),(-1,-1),1.5,red),
                        ('LINEABOVE',(0,0),(-1,-1),1.5,red),
                        ('LINEAFTER',(0,0),(-1,-1),1.5,red),
                    ]
                )

class paged:
    story=[]
    def __init__(self):
        self.styling=styles()
    
    def ls(self,dir):
        return os.listdir(dir)
       
    def columnate(self,fnames,dir,chunks=2,X=3.5,Y=3.5):
        return [[Image(os.path.join(dir,x),X*inch,Y*inch) for x in fnames[i:i+chunks]] for i in range(0,len(fnames),chunks)]

    def mktable(self,dir):
        colsPre=self.columnate(self.ls(dir),dir)
        tbls=Table(colsPre)
        tbls.setStyle(self.styling.defaultTableCenter)
        return tbls

    def pageNum(self,canvas,doc):
        pageNum=canvas.getPageNumber()
        text="Page {}".format(pageNum)
        canvas.setFont('Times-Bold',12)
        canvas.drawString(letter[0]-50,letter[1]-(letter[1]-20),text)

    def doc_init(self,title):
        doc=SimpleDocTemplate(title,pagesize=letter,
                rightMargin=25,
                leftMargin=25,
                topMargin=25,
                bottomMargin=25)
        doc.title=os.path.basename(title)
        return doc,[]

    def build(self,doc):
        try:
            doc.build(self.story,onFirstPage=self.pageNum,onLaterPages=self.pageNum)
            return True
        except Exception as e:
            err=sys.exc_info()[0]
            print(e)
            if err == reportlab.platypus.doctemplate.LayoutError:
                print('check your entries! not all entries will fit together!: "{}"'.format(e))
            return False

    def tasks(self,docName,qrcode_dir):
        doc,self.story=self.doc_init(docName) 
        self.story.append(self.mktable(qrcode_dir))
        self.build(doc)
if __name__ == "__main__":
    p=paged()
    p.tasks('codes_test.pdf','./qrcodes')

