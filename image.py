
def snapshot(img, base_coords):
	print('beginning snapshot')
	width=175
	height=175
	area = [int(base_coords[0])-width, int(base_coords[1])-height, int(base_coords[0])+width, base_coords[1]+height]
	for index, i in enumerate(area):
		if i < 0:
			area[index] = 0
	area2 = tuple(area)
	print(f"Final area coords: {area2}")
	img2 = img.crop(area2)
	img2.save("snapshot.png")
	
def pattern_pixel(x, y, pattern, inverted):
    sign = -1 if inverted else 1
    # Diagonal
    if pattern == 1:
        return (x-sign*y) % 7 == 0 or (x-sign*y) % 7 == 1 or (x-sign*y) % 7 == 2
    #Vertical
    elif pattern == 2:
        return x % 7 == 0 or x % 7 == 1 or x % 7 == 2
    #Horizontal
    elif pattern == 3:
        return y % 7 == 0 or y % 7 == 1 or y % 7 == 2
    #Glass
    elif pattern == 4:
        return sign*(x * y) % 7 == 0 or sign*(x * y) % 7 == 1
    #Bones
    elif pattern == 5:
        return sign*(x * y) % 7 == 2
    #Ovals
    elif pattern == 6:
        return sign*(x * y) % 8 == 2 or sign*(x * y) % 8 == 3
    #Amoeba
    elif pattern == 7:
        return sign*(x * y) % 8 == 2 or sign*(x * y) % 8 == 3 or sign*(x * y) % 8 == 4
    #Footballs
    elif pattern == 8:
        return sign * (x * y) % 7 == 2 or sign * (x * y) % 7 == 1
    #Circles
    elif pattern == 9:
        return (x+y) % 7 == 0 or (x+y) % 7 == 1 or (x-y) % 7 == 0 or (x-y) % 7 == 1
    #Diamonds
    elif pattern == 10:
        return (x + y) % 9 == 0 or (x - y) % 9 == 0 or (x + y) % 9 == 1 or (x - y) % 9 == 1
    #Chain
    elif pattern == 11:
        return round(5*math.sin(x)*math.cos(y)) % 7 == 2
    #Chcolate Bar
    elif pattern == 12:
        return round(5 * math.sin(x) * math.cos(y)) % 7 == 0
    #Graph Paper
    elif pattern == 13:
        return x % 9 == 0 or y % 9 == 0
    #Royal
    elif pattern == 14:
        return round(2*(math.sin(y) + math.sin(x))) % 2 == 1
    #Acid
    elif pattern == 15:
        return round(3*(math.sin(y) + math.sin(x))) % 2 == 1
    return False


def quick_fill(image_reference, xy, value, pattern=None, pattern_color=(255, 255, 255, 255), inverted_pattern=False):
    if 0 <= xy[0] < image_reference.size[0] and 0 <= xy[1] < image_reference.size[1] and value != image_reference.getpixel(xy):
        _quick_fill(image_reference, xy[0], xy[1], value, image_reference.getpixel(xy), pattern, pattern_color, inverted_pattern)


def _quick_fill(image_reference, x, y, value, selected_color, pattern, pattern_color, inverted_pattern):
    while True:
        original_x = x
        original_y = y
        while y != 0 and image_reference.getpixel((x, y-1)) == selected_color:
            y -= 1
        while x != 0 and image_reference.getpixel((x-1, y)) == selected_color:
            x -= 1
        if x == original_x and y == original_y:
            break
    quick_fill_core(image_reference, x, y, value, selected_color, pattern, pattern_color, inverted_pattern)


def quick_fill_core(image_reference, x, y, value, selected_color, pattern, pattern_color, inverted_pattern):
    last_row_length = 0
    while True:
        row_length = 0
        start_x = x
        if last_row_length != 0 and image_reference.getpixel((x, y)) != selected_color:
            while True:
                last_row_length -= 1
                if last_row_length == 0:
                    return
                x += 1
                if not(image_reference.getpixel((x, y)) != selected_color):
                    break
            start_x = x
        else:
            while x != 0 and image_reference.getpixel((x-1, y)) == selected_color:
                x -= 1
                image_reference.putpixel((x, y), (pattern_color if pattern_pixel(x, y, pattern, inverted_pattern) else value))
                if y != 0 and image_reference.getpixel((x, y-1)) == selected_color:
                    _quick_fill(image_reference, x, y-1, value, selected_color, pattern, pattern_color, inverted_pattern)
                row_length += 1
                last_row_length += 1
        while start_x < image_reference.size[0] and image_reference.getpixel((start_x, y)) == selected_color:
            image_reference.putpixel((start_x, y), (pattern_color if pattern_pixel(start_x, y, pattern, inverted_pattern) else value))
            row_length += 1
            start_x += 1
        if row_length < last_row_length:
            end = x + last_row_length
            start_x += 1
            while start_x < end:
                if image_reference.getpixel((start_x, y)) == selected_color:
                    quick_fill_core(image_reference, start_x, y, value, selected_color, pattern, pattern_color, inverted_pattern)
                start_x += 1
        elif row_length > last_row_length and y != 0:
            end = x + last_row_length
            end += 1
            while end < start_x:
                if image_reference.getpixel((end, y-1)) == selected_color:
                    _quick_fill(image_reference, end, y-1, value, selected_color, pattern, pattern_color, inverted_pattern)
                end += 1
        last_row_length = row_length
        y += 1
        if not (last_row_length != 0 and y < image_reference.size[1]):
            break
 
