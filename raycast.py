import pygame
import math
import time

class Ray:
	def __init__(self, startx, starty, endx, endy):
		self.startx = startx
		self.starty = starty
		self.endx = endx
		self.endy = endy

class Structure:
	def __init__(self, startx, starty, endx, endy):
		self.startx = startx
		self.starty = starty
		self.endx = endx
		self.endy = endy

class Player:
	def __init__(self, x, y, w, dist = 400, fov = 70, direction = 0):
		self.x = x
		self.y = y
		self.w = w
		self.dist = dist
		self.fov = fov * math.pi / 180
		self.direction = direction

		self.ang = self.fov / (self.w - 1)
		self.rays = [Ray(0, 0, 0, 0) for i in range(self.w)]
		self.offset = self.fov / 2

		self.distanses = []
		self.rotation_speed = 0.1
		self.speed = 3
		self.cell_size = 20

	def rotation(self, ang):
		self.direction += ang * self.rotation_speed

	def move(self, x, y):
		if x == 0 and y == 0: return
		elif x == -1 and y == 0: ang = math.pi / 2
		elif x == 1 and y == 0: ang = - math.pi / 2 

		elif x == 0 and y == -1: ang = 0
		elif x == -1 and y == -1: ang = math.pi / 2 - math.pi / 4
		elif x == 1 and y == -1: ang = - math.pi / 2 + math.pi / 4 

		elif x == 0 and y == 1: ang = math.pi
		elif x == -1 and y == 1: ang = math.pi / 2 + math.pi / 4
		elif x == 1 and y == 1: ang = - math.pi / 2 - math.pi / 4

		self.x += (math.cos(self.direction + ang) if x != 0 or y != 0 else 0) * self.speed
		self.y += (math.sin(self.direction + ang) if x != 0 or y != 0 else 0) * self.speed

	def get_dist(self, point1, point2):
		return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

	def render(self, structures):
		for i in range(self.w):
			self.rays[i].startx = self.x
			self.rays[i].starty = self.y

			ang = i * self.ang + self.direction - self.offset
			self.rays[i].endx = math.cos(ang) * self.dist + self.x
			self.rays[i].endy = math.sin(ang) * self.dist + self.y

		self.distanses = []
		for ray in self.rays:
			for structure in structures:

				point = self.find_intersection(
					(
						(structure.startx, structure.starty),
						(structure.endx, structure.endy)
					),
					(
						(ray.startx, ray.starty),
						(ray.endx, ray.endy)
					)
				)

				if point:
					ray.endx = point[0]
					ray.endy = point[1]

			self.distanses.append(((ray.endx - ray.startx) ** 2 + (ray.endy - ray.starty) ** 2) ** 0.5)

	def find_intersection(self, line1, line2):
		start1 = line1[0]
		start2 = line2[0]

		end1 = line1[1]
		end2 = line2[1]

		dir1 = (end1[0] - start1[0], end1[1] - start1[1])
		dir2 = (end2[0] - start2[0], end2[1] - start2[1])

		a1 = -dir1[1]
		b1 = dir1[0]
		d1 = - (a1 * start1[0] + b1 * start1[1])

		a2 = -dir2[1]
		b2 = dir2[0]
		d2 = - (a2 * start2[0] + b2 * start2[1])

		s1_l2_st = a2 * start1[0] + b2 * start1[1] + d2
		s1_l2_ed = a2 * end1[0] + b2 * end1[1] + d2

		s2_l1_st = a1 * start2[0] + b1 * start2[1] + d1
		s2_l1_ed = a1 * end2[0] + b1 * end2[1] + d1

		if (s1_l2_st * s1_l2_ed >= 0 or s2_l1_st * s2_l1_ed >= 0):
			return False

		u = s1_l2_st / (s1_l2_st - s1_l2_ed);
	
		return (start1[0] + u * dir1[0], start1[1] +  u * dir1[1])

	def draw2d(self, screen, structures):
		# Draw player
		pygame.draw.circle(screen, (255, 0, 255), (self.x, self.y), 3)

		# Draw rays
		for ray in self.rays:
			pygame.draw.line(screen, (255, 0, 0), (ray.startx, ray.starty), (ray.endx, ray.endy))

		# Draw 
		for structure in structures:
			pygame.draw.line(screen, (0, 255, 0), (ray.startx, ray.starty), (ray.endx, ray.endy))

	def draw_minimap(self, screen, structures):
		scale = 0.2

		w = screen.get_width() * scale
		h = screen.get_height() * scale

		# Background
		pygame.draw.rect(screen, (127, 127, 127, 127), ((0,0), (w, h)))

		# Player draw
		pygame.draw.circle(screen, (255, 0, 0), (self.x * scale, self.y * scale), 2)

		# Player direction
		x1, y1, x2, y2 = self.x * scale, self.y * scale, self.x + math.cos(self.direction) * self.dist, self.y + math.sin(self.direction) * self.dist
		pygame.draw.line(screen, (0, 255, 255), (x1, y1), (x2 * scale, y2 * scale))

		# Structures
		for structure in structures:
			x1, y1, x2, y2 = structure.startx * scale, structure.starty * scale, structure.endx * scale, structure.endy * scale
			pygame.draw.line(screen, (0, 255, 0), (x1, y1), (x2, y2))

	def draw3d(self, screen, structures):
		screen_w, screen_h = screen.get_width(), screen.get_height()
		scale = screen_w / self.w 

		projection_distance = 0.5 * self.cell_size / math.tan(self.offset)
		previous_column = 0

		pygame.draw.rect(screen, (0, 200, 200), ((0, 0), (screen_w, screen_h // 2)))
		pygame.draw.rect(screen, (100, 100, 100), ((0, screen.get_height() // 2), (screen_w, screen_h // 2)))

		for i, length in enumerate(self.distanses):
			ray_direction = self.fov * ((0.5 * self.w) - i) / (self.w - 1)
			ray_projection_pos = 0.5 * math.tan(ray_direction) / math.tan(self.offset)

			current_column = int(screen_w * (0.5 - ray_projection_pos))

			next_column = screen_w

			if i < screen_w - 1:
				next_ray_direction = self.fov * ((0.5 * self.w) - 1 - i) / (self.w - 1)
				ray_projection_pos = 0.5 * math.tan(next_ray_direction) / math.tan(self.fov / 2)
				next_column = int(screen_w * (0.5 - ray_projection_pos))


			if previous_column < current_column:
				height = screen_h * projection_distance / (length * math.cos(ray_direction))
				color = int((math.cos(time.time()) / 2 + 0.5) * 255), (max(0, 1 - length / self.dist)) * 255, 0

				surf = pygame.Surface((
					max(scale, next_column - current_column) * scale,
					height # Size
				))

				surf.fill(color)
				surf.set_alpha( 255 - (255 * max (0, 2 * length / self.dist - 1)))
				screen.blit(surf, 
					(current_column, (screen_h - height) / 2) # Start pos (left top)
				)

				previous_column = current_column

		self.draw_minimap(screen, structures)

class Raycasting:
	def __init__(self, w = 1440, h = 900):
		self.w = w
		self.h = h
		self.screen = None
		self.player = Player(10, 10, w, 400, 70, 0.4)
		self.movex = 0
		self.movey = 0
		self.rotation = 0
		self.d3 = True

		self.structures = [
			Structure(0, 0, self.w, 0),
			Structure(0, 0, 0, self.h),
			Structure(self.w, 0, self.w, self.h),
			Structure(0, self.h, self.w, self.h),
			Structure(40, 40, 40, 80),
			Structure(40, 40, 80, 40),
			Structure(40, 80, 80, 80),
			Structure(80, 80, 80, 120),
		]

	def start(self):
		self.screen = pygame.display.set_mode((self.w, self.h))
		pygame.display.set_caption('Raycasting')
		self.enable = True

		while self.enable:
			start_t = time.time()
			s = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.enable = False

				if event.type == pygame.KEYDOWN:
					if event.key == 119:
						self.movey += -1 

					if event.key == 115:
						self.movey += 1

					if event.key == 97:
						self.movex += 1

					if event.key == 100:
						self.movex += -1

					if event.key == 113:
						self.rotation += -1

					if event.key == 101:
						self.rotation += 1

				if event.type == pygame.KEYUP:
					if event.key == 119:
						self.movey -= -1 

					if event.key == 115:
						self.movey -= 1

					if event.key == 97:
						self.movex -= 1

					if event.key == 100:
						self.movex -= -1

					if event.key == 113:
						self.rotation -= -1

					if event.key == 101:
						self.rotation -= 1

				if event.type == pygame.MOUSEMOTION:
					if s:
						continue
					left_up = event.pos[0], event.pos[1]
					center =  left_up[0] + self.w // 2, left_up[1] + self.h // 2

					s = True

			self.screen.fill((0, 0, 0))
			self.player.rotation(self.rotation)

			self.player.move(self.movex, self.movey)
			self.player.render(self.structures)

			if self.d3:
				self.player.draw3d(self.screen, self.structures)
			else:
				self.player.draw2d(self.screen, self.structures)

			pygame.display.flip()

if __name__ == '__main__':
	raycast = Raycasting()
	raycast.start()
