from OpenGL.GL import *
import math

def dda_line(x1, y1, x2, y2, color=(1, 1, 0)):
    """
    Draw a line using the Digital Differential Analyzer (DDA) algorithm.
    This is more efficient than the built-in OpenGL line drawing.
    """
    dx = x2 - x1
    dy = y2 - y1
    
    # Calculate steps based on the larger distance
    steps = max(abs(dx), abs(dy))
    
    # Calculate increment in x and y for each step
    x_increment = dx / steps
    y_increment = dy / steps
    
    # Set initial points
    x = x1
    y = y1
    
    # Begin drawing points
    # Handle both RGB and RGBA color formats
    if len(color) == 4:  # RGBA
        glColor4f(*color)
    else:  # RGB
        glColor3f(*color)
    glBegin(GL_POINTS)
    
    # Draw each point in the line
    for i in range(int(steps) + 1):
        glVertex2f(round(x), round(y))  # Round to nearest pixel
        x += x_increment
        y += y_increment
    
    glEnd()
    glColor3f(1, 1, 1)  # Reset color

def midpoint_circle(center_x, center_y, radius, color=(1, 0, 0)):
    """
    Draw a circle using the Midpoint Circle algorithm.
    More efficient than using trigonometric functions for each point.
    """
    x = 0
    y = radius
    p = 1 - radius  # Initial decision parameter
    
    # Handle both RGB and RGBA color formats
    if len(color) == 4:  # RGBA
        glColor4f(*color)
    else:  # RGB
        glColor3f(*color)
    glBegin(GL_POINTS)
    
    # Plot initial points in all octants
    plot_circle_points(center_x, center_y, x, y)
    
    # Calculate points for one octant and reflect to others
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        
        plot_circle_points(center_x, center_y, x, y)
    
    glEnd()
    glColor3f(1, 1, 1)  # Reset color

def plot_circle_points(center_x, center_y, x, y):
    """
    Plot points in all octants of a circle.
    """
    glVertex2f(center_x + x, center_y + y)
    glVertex2f(center_x - x, center_y + y)
    glVertex2f(center_x + x, center_y - y)
    glVertex2f(center_x - x, center_y - y)
    glVertex2f(center_x + y, center_y + x)
    glVertex2f(center_x - y, center_y + x)
    glVertex2f(center_x + y, center_y - x)
    glVertex2f(center_x - y, center_y - x)

def midpoint_ellipse(center_x, center_y, a, b, color=(0, 1, 0)):
    """
    Draw an ellipse using the Midpoint Ellipse algorithm.
    a: semi-major axis (horizontal radius)
    b: semi-minor axis (vertical radius)
    """
    # Handle both RGB and RGBA color formats
    if len(color) == 4:  # RGBA
        glColor4f(*color)
    else:  # RGB
        glColor3f(*color)
    glBegin(GL_POINTS)
    
    # Region 1
    x = 0
    y = b
    d1 = b*b - a*a*b + 0.25*a*a
    dx = 2*b*b*x
    dy = 2*a*a*y
    
    while dx < dy:
        plot_ellipse_points(center_x, center_y, x, y)
        
        if d1 < 0:
            x += 1
            dx += 2*b*b
            d1 += dx + b*b
        else:
            x += 1
            y -= 1
            dx += 2*b*b
            dy -= 2*a*a
            d1 += dx - dy + b*b
    
    # Region 2
    d2 = (b*b*(x+0.5)*(x+0.5) + a*a*(y-1)*(y-1) - a*a*b*b)
    
    while y >= 0:
        plot_ellipse_points(center_x, center_y, x, y)
        
        if d2 > 0:
            y -= 1
            dy -= 2*a*a
            d2 += a*a - dy
        else:
            y -= 1
            x += 1
            dx += 2*b*b
            dy -= 2*a*a
            d2 += dx - dy + a*a
    
    glEnd()
    glColor3f(1, 1, 1)  # Reset color

def plot_ellipse_points(center_x, center_y, x, y):
    """
    Plot points in all quadrants of an ellipse.
    """
    glVertex2f(center_x + x, center_y + y)
    glVertex2f(center_x - x, center_y + y)
    glVertex2f(center_x + x, center_y - y)
    glVertex2f(center_x - x, center_y - y)

def translate_point(x, y, tx, ty):
    """
    Translate a point by (tx, ty).
    """
    return x + tx, y + ty

def rotate_point(x, y, center_x, center_y, angle_degrees):
    """
    Rotate a point around a center by the given angle in degrees.
    """
    # Convert angle to radians
    angle_radians = math.radians(angle_degrees)
    
    # Translate point to origin
    x_translated = x - center_x
    y_translated = y - center_y
    
    # Rotate point
    x_rotated = x_translated * math.cos(angle_radians) - y_translated * math.sin(angle_radians)
    y_rotated = x_translated * math.sin(angle_radians) + y_translated * math.cos(angle_radians)
    
    # Translate back
    return x_rotated + center_x, y_rotated + center_y

def scale_point(x, y, center_x, center_y, sx, sy):
    """
    Scale a point relative to a center point.
    """
    # Translate to origin
    x_translated = x - center_x
    y_translated = y - center_y
    
    # Scale
    x_scaled = x_translated * sx
    y_scaled = y_translated * sy
    
    # Translate back
    return x_scaled + center_x, y_scaled + center_y

def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """
    Cohen-Sutherland line clipping algorithm.
    Returns clipped line coordinates or None if line is completely outside.
    """
    # Define region codes
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000
    
    def compute_code(x, y):
        code = INSIDE
        if x < xmin:      # to the left of clip window
            code |= LEFT
        elif x > xmax:    # to the right of clip window
            code |= RIGHT
        if y < ymin:      # below the clip window
            code |= BOTTOM
        elif y > ymax:    # above the clip window
            code |= TOP
        return code
    
    # Compute codes for the endpoints
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)
    
    # Initialize line as completely visible
    accept = False
    
    while True:
        # Both endpoints inside window - trivially accept
        if code1 == 0 and code2 == 0:
            accept = True
            break
        # Line completely outside window - trivially reject
        elif code1 & code2 != 0:
            break
        # Line needs clipping - at least one endpoint is outside
        else:
            # Select an outside point
            code_out = code1 if code1 != 0 else code2
            
            # Calculate intersection point
            x, y = 0, 0
            
            # Find intersection with clip edge
            if code_out & TOP:  # point is above the clip window
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif code_out & BOTTOM:  # point is below the clip window
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif code_out & RIGHT:  # point is to the right of clip window
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax
            elif code_out & LEFT:  # point is to the left of clip window
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin
            
            # Replace outside point with intersection point
            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)
    
    if accept:
        return x1, y1, x2, y2
    else:
        return None  # Line completely outside