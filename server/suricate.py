import logging

from typing import List
from  my_types import SessionId
from flask_socketio import join_room, leave_room, emit
from cam_controller import CamController

logger = logging.getLogger('suricate_server.' + __name__)

class Suricate:
	""" init a Suricat.

		:param sid: The session id of the suricate_cmd namespace.

	"""
	def __init__(self, sid : SessionId) -> None:

		self.id                        : SessionId = sid
		self.room                      : str = 'room_' + sid # create room name from sid
		self.suricate_cmd_sid          : SessionId = sid
		self.suricate_video_stream_sid : SessionId = SessionId('NONE')
		self.watchers                  : List[SessionId] = []
		self.cam_controler             : CamController = CamController(self)
		

	def add_watcher(self, watcher_sid : SessionId):
		#
		# add watcher to suricat room
		#
		logger.info('+ Entering room [%s]', self.room)
		join_room(sid=watcher_sid, room=self.room, namespace='/watcher_video_cast')

		# add watcher to watcher list
		self.watchers.append(watcher_sid)

		#
		# start suricate video stream
		#
		if len(self.watchers) == 1 : 
			logger.info("+ starting suricate stream: %s", self.suricate_cmd_sid)
			emit('start_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

	def remove_watcher(self, watcher_sid : SessionId):
		
		# lets leave the room
		logger.info('+ removing watcher from room <%s>', self.room)
		leave_room(sid=watcher_sid, room=self.room, namespace='/watcher_video_cast')

		# remove watcher from watcher list
		self.watchers.remove(watcher_sid)
		
		if (len(self.watchers) <= 0):
			# if no more watcher for this suricate stop video stream
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

	def start_cam_ctrl(self):
		
		logger.info("+ Suricate [%s] start cmd ctrl", self.id)
		self.cam_controler.evt_start_cam_ctrl()

	def stop_cam_ctrl(self):

		logger.debug("+ Suricate [%s] end cmd ctrl", self.id)
		self.cam_controler.evt_stop_cam_ctrl()

	def move_cam(self, vector):
		
		logger.info("+ Suricate [%s] move cam x: %.4f y: %.4f", self.id, vector['x'], vector['y'])
		self.cam_controler.evt_move_cam(vector)
		 
	def do_start_cam_ctrl(self):

		logger.debug("+ Suricate [%s] start cmd ctrl", self.id)
		self.is_cam_in_use = True
		emit('start_cam_ctrl', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)
	
	def do_stop_cam_ctrl(self):

		logger.debug("+ Suricate [%s] start cmd ctrl", self.id)
		self.is_cam_in_use = False
		emit('stop_cam_ctrl', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)
	
	def do_move_cam(self, data):

		logger.debug("+ Suricate [%s] start move cam", self.id)
		
		emit('move_cam', data, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

