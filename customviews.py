import ui
from objc_util import *


class DisplayCIImage(ui.View):
    '''
    Display a CIImage as a UIImage
    class has two properties that need to be set each time a UIImage is drawn
        ci_img: the CIImage to display (initially set to photosplash.png)
        rect: a CGRect that is the size of the UIImage to display (initially 
              set to ((0.0, 0.0), (640, 427)) )
      In addition, when a new image is loaded, frame.height and frame.width should be set to the original size of the image
    '''
    def __init__(self, *args, **kwargs):
        '''
        Set a (reusable) drawing context and provide default values for the image and image size
        '''
        super().__init__(*args, **kwargs)
        CIContext = ObjCClass('CIContext')
        self._ctx = CIContext.contextWithOptions_(None)
        ci_img = ObjCClass('CIImage').imageWithContentsOfURL_(nsurl('photosplash.png'))
        self.rect = CGRect((0.0, 0.0), (640, 427))
        self.ci_img = ci_img
        
    def draw(self):
        '''
        Redraw the UIImage by calling the method set_needs_display on the
        instance of the class
        '''        
        cg_img = self._ctx.createCGImage_fromRect_(self.ci_img,
                                                   self.ci_img.extent())
        self.ui_img = UIImage.imageWithCGImage_scale_orientation_(cg_img, 1.0, 0)
        c.CGImageRelease.argtypes = [c_void_p]
        c.CGImageRelease.restype = None
        c.CGImageRelease(cg_img)        
        self.ui_img.drawInRect_(self.rect)

class DisplayHistogram(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CIContext = ObjCClass('CIContext')
        self._ctx = CIContext.contextWithOptions_(None)
        #self.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
        self.CIVector = ObjCClass('CIVector')
        CIFilter = ObjCClass('CIFilter')
        self.CIAreaHistogram = CIFilter.filterWithName_('CIAreaHistogram')
        self.CIHistogramDisplayFilter = CIFilter.filterWithName_('CIHistogramDisplayFilter')
        ci_img = ObjCClass('CIImage').imageWithContentsOfURL_(nsurl('20160730_152103.jpg'))
        self.ci_img = ci_img
        
    def draw(self):
        c.CGAffineTransformMakeScale.argtypes = [c_double, c_double]
        c.CGAffineTransformMakeScale.restype = CGAffineTransform
        transform = c.CGAffineTransformMakeScale(c_double(0.1), c_double(0.1))
        self.scaled_img = self.ci_img.imageByApplyingTransform_(transform)
        self.CIAreaHistogram.setDefaults()
#        self.CIAreaHistogram.setValue_forKey_(self.ci_img, 'inputImage')
        self.CIAreaHistogram.setValue_forKey_(self.scaled_img, 'inputImage')
        self.CIAreaHistogram.setValue_forKey_(256, 'inputCount')
        vec = self.CIVector.vectorWithCGRect_(self.scaled_img.extent())
        self.CIAreaHistogram.setValue_forKey_(vec, 'inputExtent')
        self.CIAreaHistogram.setValue_forKey_(25.0, 'inputScale')
        self.area_img = self.CIAreaHistogram.valueForKey_('outputImage')
        self.CIHistogramDisplayFilter.setDefaults()
        self.CIHistogramDisplayFilter.setValue_forKey_(100.0, 'inputHeight')
        self.CIHistogramDisplayFilter.setValue_forKey_(1.0, 'inputHighLimit')
        self.CIHistogramDisplayFilter.setValue_forKey_(self.area_img, 'inputImage')
        self.disp_img = self.CIHistogramDisplayFilter.valueForKey_('outputImage')
        cg_img = self._ctx.createCGImage_fromRect_(self.disp_img,
                                                   self.disp_img.extent())
        self.ui_img = UIImage.imageWithCGImage_scale_orientation_(cg_img, 1.0, 0)
        c.CGImageRelease.argtypes = [c_void_p]
        c.CGImageRelease.restype = None
        c.CGImageRelease(cg_img)
        self.ui_img.drawInRect_(CGRect((0.0, 0.0), (256, 100)))
        

class FiltersView(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.name is not None:
            title_label = ui.Label(text=self.name,
                                   frame=(10, 0, 275, 25),
                                   alignment=ui.ALIGN_CENTER,
                                   font =('<system-bold>', 18))
            self.add_subview(title_label)

    
class SliderWithValueLabel(ui.View):
    def __init__(self, slider_name, convert, action, valuefmt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._m = convert['m']
        self._b = convert['b']
        self._valuefmt = valuefmt
        self.changed = action
        self.name = slider_name
        SLIDER_WIDTH = 200
        SLIDER_HEIGHT = 30
        SLIDER_TITLE_OFFSET = 25
        SLIDER_TITLE_WIDTH = 200
        SLIDER_TITLE_HEIGHT = 25
        SLIDER_VALUE_OFFSET = 10
        SLIDER_VALUE_HEIGHT = 25
        SLIDER_VALUE_WIDTH = 50
        self.border_width = 0
        self.border_color = 'black'
        self._slider = ui.Slider(frame=(0, SLIDER_TITLE_OFFSET, SLIDER_WIDTH, SLIDER_HEIGHT))
        self._slider.continuous = False
        self._slider.value = 0.5
        self._slider.action = self.update        
        slider_title = ui.Label(frame=(0, 0, SLIDER_TITLE_WIDTH, SLIDER_TITLE_HEIGHT))
        slider_title.text = slider_name
        slider_title.text_color = 'black'
        self._slider_valuelabel = ui.Label(frame=(SLIDER_WIDTH + SLIDER_VALUE_OFFSET, SLIDER_TITLE_OFFSET, SLIDER_VALUE_WIDTH, SLIDER_VALUE_HEIGHT))
        self._slider_valuelabel.text = str(0.5)
        self._slider_valuelabel.border_width = 1
        self._slider_valuelabel.border_color = 'black'
        self._slider_valuelabel.alignment = ui.ALIGN_CENTER
        self.add_subview(self._slider)
        self.add_subview(slider_title)
        self.add_subview(self._slider_valuelabel)
        
    def initialize(self, value):
        self.value = value
        self._slider_valuelabel.text = self._valuefmt.format(self.value)
        self._slider.value = (value - self._b) / self._m
        
    def update(self, sender):
        self.value = self._m * sender.value + self._b
        self._slider_valuelabel.text = self._valuefmt.format(self.value)
        if self.changed and callable(self.changed):
            self.changed(self)
