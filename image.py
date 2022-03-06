## Rusty's Dot Map Function updated with / commands. Can I learn it and make it work within the new bot's structure?
@slash.slash(name="dotmap", description="prints dots with unique colors corresponding to each province they are a part of", guild_ids=servers)
async def dot_map(self, ctx):
        province_map = Image.open("./original_map.png").convert("RGBA")
        province_map_rgb = province_map.convert("RGB")
        with open("./province_data.json", "r") as f:
            province_data = json.load(f)
        for province in province_data:
            for area in province_data[province]["coordinates"]:
                province_map_rgb.putpixel(make_tuple(area), (255, 0, 0, 255))
        province_map_rgb.save("./test_map.png")
        await ctx.send(file=discord.File("./test_map.png"))

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
	
def quick_fill(image_reference, xy, value):
    if 0 <= xy[0] < image_reference.size[0] and 0 <= xy[1] < image_reference.size[1] and value != image_reference.getpixel(xy):
        _quick_fill(image_reference, xy[0], xy[1], value, image_reference.getpixel(xy))


def _quick_fill(image_reference, x, y, value, selected_color):
    while True:
        original_x = x
        original_y = y
        while y != 0 and image_reference.getpixel((x, y-1)) == selected_color:
            y -= 1
        while x != 0 and image_reference.getpixel((x-1, y)) == selected_color:
            x -= 1
        if x == original_x and y == original_y:
            break
    quick_fill_core(image_reference, x, y, value, selected_color)


def quick_fill_core(image_reference, x, y, value, selected_color):
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
                image_reference.putpixel((x, y), value)
                if y != 0 and image_reference.getpixel((x, y-1)) == selected_color:
                    _quick_fill(image_reference, x, y-1, value, selected_color)
                row_length += 1
                last_row_length += 1
        while start_x < image_reference.size[0] and image_reference.getpixel((start_x, y)) == selected_color:
            image_reference.putpixel((start_x, y), value)
            row_length += 1
            start_x += 1
        if row_length < last_row_length:
            end = x + last_row_length
            start_x += 1
            while start_x < end:
                if image_reference.getpixel((start_x, y)) == selected_color:
                    quick_fill_core(image_reference, start_x, y, value, selected_color)
                start_x += 1
        elif row_length > last_row_length and y != 0:
            end = x + last_row_length
            end += 1
            while end < start_x:
                if image_reference.getpixel((end, y-1)) == selected_color:
                    _quick_fill(image_reference, end, y-1, value, selected_color)
                end += 1
        last_row_length = row_length
        y += 1
        if not (last_row_length != 0 and y < image_reference.size[1]):
            break
