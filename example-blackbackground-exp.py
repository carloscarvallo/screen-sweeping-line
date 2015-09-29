#!/usr/bin/python
from pymouse import PyMouse
import gtk
import gobject
import cairo

DELAY = 9
DELTA = 1

class MyApp():

    def __init__(self):
        window = gtk.Window()
        window.set_decorated(False)

	screen = window.get_screen()
	self.WIDTH = screen.get_width()
	self.HEIGHT = screen.get_height()

	window.set_default_size(self.WIDTH, self.HEIGHT)
	#window.set_app_paintable(True)

	self.DELTA_X = DELTA
        self.DELTA_Y = DELTA

	# Variable global que ira indicando el "indice" de pixel donde dibujar
        # la linea vertical
        self._x = 0
        
        # Variable global que contendra el "indice" de pixel donde el usuario
        # presiono alguna tecla para detenerlo. El valor inicial -1 indica que
        # todavia no se ha presionado una tecla para la linea vertical
        self._selected_x = -1
            
        # Variable global que ira indicando el "indice" de pixel donde dibujar
        # la linea horizontal
        self._y = 0
        
        # Variable global que contendra el "indice" de pixel donde el usuario
        # presiono alguna tecla para detenerlo. El valor inicial -1 indica que
        # todavia no se ha presionado una tecla para la linea horizontal
        self._selected_y = -1

        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.set_size_request(self.WIDTH, self.HEIGHT)

        window.connect('destroy', self.destroy)
	window.connect('screen-changed', self.screen_changed)
        self.drawing_area.connect('configure_event', self.__configure_cb)
        self.drawing_area.connect('expose-event', self.__expose_cb)
	window.connect('key-press-event', self.__key_press_cb, self.drawing_area)

        window.add(self.drawing_area)
	
	self.screen_changed(window)
        
        window.show_all()

	gobject.timeout_add(DELAY, self.__move_vertical_line, self.drawing_area)

    def destroy(self, window, data=None):
        gtk.main_quit()
	
    def screen_changed(self, widget, data=None):
    	
    	# To check if the display supports alpha channels, get the colormap
    	screen = widget.get_screen()
    	colormap = screen.get_rgba_colormap()
    
    	# Now we have a colormap appropriate for the screen, use it
    	widget.set_colormap(colormap)
    
	return False

    def __configure_cb(self, drawing_area, data=None):
        x, y, width, height = drawing_area.get_allocation()
        
        canvas = drawing_area.window

        self.pixmap = gtk.gdk.Pixmap(canvas, width, height)

        return True

    def __expose_cb(self, drawing_area, data=None):
        x, y, width, height = data.area
        self.context = drawing_area.get_style().fg_gc[gtk.STATE_NORMAL]

        canvas = drawing_area.window
        
        canvas.draw_drawable(self.context, self.pixmap, x, y, x, y, width, height)

        return False

    def __key_press_cb(self, window, event, drawing_area):
        # Al presionar cualquier tecla, determinar la accion a tomar, de 
        # acuerdo al estado de las lineas.
        if self._selected_x == -1:
            self._selected_x = self._x
            gobject.timeout_add(DELAY, self.__move_horizontal_line, drawing_area)            
        elif self._selected_y == -1:
            self._selected_y = self._y
            gobject.timeout_add(DELAY, self.draw_arc, window)
        else:
            self.restart_game(drawing_area, window)

    def __move_vertical_line(self, drawing_area):
        #Dibujar el fondo sobre el cual movemos las lineas, si aun no hemos
        #presionado un boton para dejar la linea vertical en una coordenada dada
        if self._selected_x < 0:
            self.draw_background(drawing_area)
        
        # Mover el indice x para que aparente movimiento
        self._x += self.DELTA_X;
        if self._x > self.WIDTH:
            self.DELTA_X *= -1
        elif self._x < 0:
            self.DELTA_X *= -1

        # Dibujar una linea vertical en la x correspondiente
        self.draw_line(drawing_area, "VERTICAL", self._x)
        
        # Si aun no se selecciono un indice para x, seguir permitiendo invocar
        # al timer. Caso contrario, retornar False para evitar mas invocaciones
        if self._selected_x < 0:
            return True
        else:
            return False

    def __move_horizontal_line(self, drawing_area):
        #Dibujar el fondo sobre el cual movemos las lineas
        self.draw_background(drawing_area)

        # Como la linea vertical ya se detuvo para poder mover la linea 
        # horizontal, dibujar la linea vertical en la x seleccionada
	self.draw_line(drawing_area, "VERTICAL", self._selected_x)

        # Mover el indice y para que aparente movimiento
	self._y += self.DELTA_Y;
	if self._y > self.HEIGHT:
	    self.DELTA_Y *= -1
	elif self._y < 0:
            self.DELTA_Y *= -1

        # Dibujar una linea horizontal en la y correspondiente
        self.draw_line(drawing_area, "HORIZONTAL", self._y)

        # Si aun no se selecciono un indice para y, seguir permitiendo invocar
        # al timer. Caso contrario, retornar False para evitar mas invocaciones
        if self._selected_y < 0:
            return True
        else:
            return False

    def draw_background(self, drawing_area):
        #Utilizado para dibujar objetos en el pixmap
        cr = self.pixmap.cairo_create()
	        
	cr.set_source_rgba(1.0, 1.0, 1.0, 0)      
        cr.set_operator(cairo.OPERATOR_SOURCE)
    	cr.paint()
	
        #drawing_area.queue_draw() 

    def draw_line(self, drawing_area, orientation, line_index):
        #Utilizado para dibujar objetos en el pixmap
        cr = self.pixmap.cairo_create()

        # Dibujar una linea que ocupe toda la pantalla y sea de
        # color blanco para contrastarlo con la diana
        cr.set_source_rgba(0, 0, 0, 1)

        if orientation == "VERTICAL":
            rectangle = gtk.gdk.Rectangle(line_index, 0, 1, self.HEIGHT)
        else:
            rectangle = gtk.gdk.Rectangle(0, line_index, self.WIDTH, 1)

        rectangle = cr.rectangle(rectangle)
        drawing_area.queue_draw() 
        cr.fill()

    def draw_arc(self, window):
        #self.drawing_area.window.draw_arc(self.context, False, self._x, self._y, 70, 70, 0, 360*64)
	window.set_keep_below(True)
	window.hide()
	m = PyMouse()
	m.move(self._x, self._y)
	m.click(self._x, self._y, 1)
	#window.set_keep_below(True)

    def restart_game(self, drawing_area, window):
	window.set_keep_above(True)
	window.show()
        self._x = self._y = 0
        self._selected_x = self._selected_y = -1 
        gobject.timeout_add(DELAY, self.__move_vertical_line, drawing_area)


if __name__ == "__main__":
    my_app = MyApp()
    gtk.main()
