# coding: utf8
import urllib2
from PIL import Image, ImageDraw, ImageFont
import base64
import sys
import pygame
import StringIO
reload(sys)
sys.setdefaultencoding('utf8')

class ImageMark():
	"""docstring for ImageMark"""
	def __init__(self):
		pass
	# def imagettfbbox(self,size,text,ttf="./library/fonts/华文细黑.ttf",method = "box"):
	#     proc = subprocess.Popen(["php -f /home/jon/root/ershixiong_auto/EsxSpider/imagettfbbox.php "+method+" "+str(size)+" "+ttf + " " + text], shell=True, 
	#     stdout=subprocess.PIPE)
	#     return json.loads(proc.stdout.read())
	
	def add_num(self,img,ttf_file):
	    draw = ImageDraw.Draw(img)
	    myfont = ImageFont.truetype(ttf_file, size=80)
	    fillcolor = "#f9f9f9"
	    width, height = img.size
	    tx = '师傅 2017-12-12 19:20:20'
	    x = width-(len(tx)*30)
	    y = height-60
	    draw.text((x, y), unicode(tx,'utf-8'), font=myfont,fill=fillcolor)
	    img.save('result.jpg','jpeg')
	
	    return 0
	
	def mark(self,text,fontsize,ttf_file):
		pygame.init()
		font = pygame.font.Font(ttf_file, fontsize)
		rtext = font.render(text, True, (255, 255, 255), (73, 73, 73))
		mark = Image.new("RGB", (rtext.get_width(), rtext.get_height()), (0, 0, 0))
		sio = StringIO.StringIO()
		pygame.image.save(rtext, sio)
		sio.seek(0)
		line = Image.open(sio)
		mark.paste(line, (0, 0))

		return mark
	
	def base64Img(self,filename = "./result.jpg"):
		file=open(filename,'rb')
		imgdata=base64.b64encode(file.read())
		file.close()
		return imgdata
	
	def aux_mark(self,ttf_file,link,text1,text2,fontsize = 14):
		opener = urllib2.build_opener()
		req = opener.open(link)
		im = Image.open(req)
		mark = self.mark(text1,fontsize,ttf_file)
		mark2 = self.mark(text2,fontsize,ttf_file)
		layer=Image.new('RGBA', im.size, (0,0,0,0))
		layer.paste(mark, (im.size[0]-mark.size[0]-5,im.size[1]-mark.size[1]-25*2))
		layer.paste(mark2, (im.size[0]-mark2.size[0]-5,im.size[1]-mark2.size[1]-25))
		out=Image.composite(layer,im,layer)
		# out.save(str(x) + '.jpg','jpeg')
		buffer = StringIO.StringIO()
		out.save(buffer, format="JPEG")
		# return base64.b64encode(buffer.getvalue())
		contens = buffer.getvalue()
		buffer.close()
		return contens
