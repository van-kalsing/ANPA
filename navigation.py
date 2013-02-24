﻿from bge       import logic
from mathutils import Vector, Matrix
from ship      import set_ship_engine_force
import math



class TargetCollection:
	def __init__(self):
		self.current_target_number = 0
		self.targets               = []
		
		
		scene   = logic.getCurrentScene()
		targets = \
			[[30, 30, -5], [-30, -30, 0], [30, -30, -5], [-30, 30, 0]]
			
		for target in targets:
			target_marker               = scene.addObject("Target_marker", "Target_marker")
			target_marker.worldPosition = target
			
			self.targets.append((target, target_marker))			
			
			
	def has_unconfirmed_targets(self):
		return self.current_target_number < len(self.targets)
		
	def get_current_target(self):
		if self.current_target_number < len(self.targets):
			target, _ = self.targets[self.current_target_number]
			
			return target
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
	def confirm_current_target(self):
		if self.current_target_number < len(self.targets):
			_, target_marker           = self.targets[self.current_target_number]
			self.current_target_number = self.current_target_number + 1
			
			if not target_marker.invalid:
				target_marker.endObject()
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
targets = TargetCollection()



def update_ship_engines_forces():
	scene         = logic.getCurrentScene()
	ship          = scene.objects["Ship"]
	target_marker = scene.objects["Target_marker"]
	
	
	
	# Определение цели
	has_target = False
	
	while targets.has_unconfirmed_targets():
		target                           = targets.get_current_target()
		distance, _, local_target_course = ship.getVectTo(target)
		
		if distance < 1:
			targets.confirm_current_target()
		else:
			has_target = True
			break
			
			
			
	# Вычисление сил винтов
	if has_target:
		target_marker.worldPosition = target
		target_marker.setVisible(True, False)
		
		
		horizontal_angle = math.asin(local_target_course.x / local_target_course.magnitude)
		if local_target_course.y < 0:
			if horizontal_angle >= 0:
				horizontal_angle = math.pi - horizontal_angle
			else:
				horizontal_angle = -math.pi - horizontal_angle
				
				
		if horizontal_angle > (math.pi / 2):
			relative_right_engine_force = -1 / (1 + math.exp(-8 * (horizontal_angle - 3 * math.pi / 4)))
		#elif horizontal_angle > 0:
		#	relative_right_engine_force = 0.5 / (1 + 1 * math.exp(horizontal_angle))
		else:
			relative_right_engine_force = 1 / (1 + math.exp(5 * (horizontal_angle - math.pi / 4)))
			
		if horizontal_angle < (-math.pi / 2):
			relative_left_engine_force = -1 / (1 + math.exp(-8 * (-horizontal_angle - 3 * math.pi / 4)))
		else:
			relative_left_engine_force = 1 / (1 + math.exp(5 * (-horizontal_angle - math.pi / 4)))
			
		relative_top_engine_force = \
			2 / (1 + 1 * math.exp(-5 * distance * local_target_course.z)) - 1
	else:
		relative_right_engine_force = 0
		relative_left_engine_force  = 0
		relative_top_engine_force   = 0
		
		
		
	# Установка сил винтов
	set_ship_engine_force("right_engine", relative_right_engine_force)
	set_ship_engine_force("left_engine",  relative_left_engine_force)
	set_ship_engine_force("top_engine", relative_top_engine_force)
	