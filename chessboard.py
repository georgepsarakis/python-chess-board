#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import signal
import re
from string import ascii_uppercase
from time import time
from random import randint
import argparse
import select

''' Helper Functions '''
def x(code = 0):
  sys.exit(code)
''' ############### '''

class Piece(object):
  '''
  Object model of a chess piece
  
  We keep information on what kind of movements the piece is able to make (straight, diagonal, gamma),
  how many squares it can cross in a single move, its type (of course) and the color (white or black).     
  '''
  DirectionDiagonal = False
  DirectionStraight = False
  DirectionGamma = False
  LeapOverPiece = False
  MaxSquares = 0
  Color = None
  Type = None
  AvailableTypes = [ 'Rook', 'Knight', 'Pawn', 'King', 'Queen', 'Bishop' ]
  Types_Direction_Map = {
      'Rook'   : [ 'straight' ],
      'Knight' : [ 'gamma' ],
      'Pawn'   : [ 'straight' ],
      'King'   : [ 'straight', 'diagonal' ],
      'Queen'  : [ 'straight', 'diagonal' ],
      'Bishop' : [ 'diagonal' ]
    }
  Types_MaxSquares_Map = {
    'Rook'   : 0,
    'Pawn'   : 1,
    'King'   : 1,
    'Queen'  : 0,
    'Bishop' : 0,
    'Knight' : -1,
  }

  def __init__(self, **kwargs):
    ''' Constructor for a new chess piece '''
    self.Type = kwargs['Type']
    ''' Perform a basic check for the type '''
    if not self.Type in self.AvailableTypes:
      raise Exception('Unknown Piece Type')
      x(1)
    self.Color = kwargs['Color']
    directions = self.Types_Direction_Map[self.Type]
    ''' Check allowed directions for movement '''
    self.DirectionDiagonal = 'diagonal' in directions
    self.DirectionGamma = 'gamma' in directions
    self.DirectionStraight = 'straight' in directions
    ''' Determine if there is a limitation on the number of squares per move '''
    self.MaxSquares = self.Types_MaxSquares_Map[self.Type]
    ''' Only Knights can move over other pieces '''
    if self.Type == 'Knight':
      self.LeapOverPiece = True

  def __str__(self):
    ''' Returns the piece's string representation: color and type '''
    return self.Color[0].lower() + self.Type[0].upper()
        
class Square(object):
  '''
  Object model of a board square

  Requires zero-based row & column indexes.
  The Piece variable holds an instance of Piece class,
  representing a piece occupying the square.
  '''
  Row = 0
  Column = 0
  Occupied = False
  Piece = None

  def __init__(self, row, column):
    ''' Square constructor requires zero-based row & column indexes '''
    self.Row = row
    self.Column = column

  def is_occupied(self):
    ''' Returns True if the square has a piece attached to it, False otherwise '''
    return self.Occupied

  def set_piece(self, piece):
    ''' Sets the piece for a square and resets the Occupied variable accordingly '''
    if piece is None:
      self.Occupied = False
    else:
      self.Occupied = True
    self.Piece = piece

  def get_piece(self):
    ''' Getter method to return the piece attached to this square instance '''
    return self.Piece

  @staticmethod
  def row_index(row):
    ''' static method that returns the zero-based row index '''
    return int(row) - 1
  
  @staticmethod
  def column_index(col):
    ''' static method that returns the zero-based column index '''
    try:
      col = int(col) - 1
    except:
      col = ascii_uppercase.index(col)
    return col

  @staticmethod
  def index_column(col):
    ''' static method that returns the column letter from zero-based column index '''
    return ascii_uppercase[col]

  @staticmethod
  def position(row, col):
    ''' 
    static method to convert zero-indexed integer coordinates to board notation 
    e.g. (0,1) -> "B1"
    '''
    return ascii_uppercase[int(col)] + str(int(row) + 1)
        
  def __str__(self):
    ''' 
    Return a string representation of the square.
    If it is occupied then return the piece info as well.
    '''
    if self.Piece is None:
      piece = ""
    else:
      piece_color = str(self.Piece)
    properties = {
        'piece'  : piece,
        'row'    : self.Row + 1,
        'column' : ascii_uppercase[self.Column],
      }
    return '%(piece)s(%(column)s%(row)d)' % properties

class Board(object):
  '''
  Object model of the board

  Described by a dictionary which keys are square positions 
  in their string representations (e.g. A1),
  and values the corresponding Square instances.
  '''
  Squares = {}
  ''' The initial setup of the board. '''
  Setup = {
      'Pawn'   : 'A2:H2|A7:H7',
      'Rook'   : 'A1,H1|A8,H8',
      'Bishop' : 'C1,F1|C8,F8',
      'Knight' : 'B1,G1|B8,G8',
      'King'   : 'E1|E8',
      'Queen'  : 'D1|D8',
    }  

  def __init__(self):
    for i in range(8):
      for j in range(8):
        self.Squares[Square.position(i, j)] = Square(i, j)

  def setup(self):
    for piece_type, piece_range in self.Setup.iteritems():
      white, black = piece_range.split('|')
      for p in self.parse_range(white):
        self.add_piece('white', piece_type, p[0], p[1])
      for p in self.parse_range(black):
        self.add_piece('black', piece_type, p[0], p[1])
 
  def parse_range(self, r):
    distinct = not ( ':' in r )
    separator = None
    if ':' in r:
      separator = ':'
    elif ',' in r:
      separator = ','
    if separator is None:
      r = [ r ]
    else:
      r = r.split(separator)
    if distinct:
      return [ ( Square.row_index(p[1]), Square.column_index(p[0]), ) for p in r ]
    else:
      start_column = Square.column_index(r[0][0])
      stop_column = Square.column_index(r[1][0])
      start_row = Square.row_index(r[0][1])
      stop_row = Square.row_index(r[1][1])
      r = []
      for column in range(start_column, stop_column - start_column + 1):
        r.append( ( start_row, column, ) )
      return r
  
  def add_piece(self, color, piece_type, row, column):    
    self.Squares[Square.position(row, column)].set_piece(Piece(Type=piece_type, Color=color))

  def __str__(self):
    column_display = '  %s  '*8 % tuple( [ Square.index_column(c) for c in list(range(8)) ] )
    board_display = "  %s\n" % (column_display,)
    board_display += '  ' + '-'*len(column_display) + "\n"
    for row in range(7, -1, -1):
      row_display = str(row + 1)
      for col in range(8):
        if self.Squares[Square.position(row, col)].is_occupied():
          piece = str(self.Squares[Square.position(row, col)].get_piece())
        else:
          piece = "  "
        row_display += '| %s ' % (piece,)
      row_display += "| %d\n" % (row + 1,)
      board_display += row_display
      board_display += '  ' + '-'*len(column_display) + "\n"
    board_display += ' ' + column_display
    return board_display
                     
class Game(object):
  board = None
  user_white = None
  user_black = None  
  CurrentPlayer = 'white'
  Timers = {
      'white' : {
        'timer'     : 0,
        'first_run' : True,
      },
      'black' : {
        'timer'     : 0,
        'first_run' : True,
      }
    }

  def __init__(self, arguments):
    '''
    Game object model    
    '''
    if randint(1, 2) == 1:
      self.user_white = arguments.user1
      self.user_black = arguments.user2
    else:
      self.user_white = arguments.user2
      self.user_black = arguments.user1
    self.board = Board()

  def time_format(self, t, user, start_time):
    current = int(t - start_time) + self.Timers[user]['timer']
    minutes = current/60
    seconds = current - 60*minutes
    if minutes < 10:
      minutes = '0' + str(minutes)
    if seconds < 10:
      seconds = '0' + str(seconds)
    return str(minutes) + ':' + str(seconds)

  def parse_time(self, t):
    t = t.split(':')
    return int(t[0])*60 + int(t[1])

  def start_timer(self):
    user = self.CurrentPlayer
    if user == 'white':
      display_username = self.user_white
    else:
      display_username = self.user_black
    print 'NOW PLAYING: %s' % display_username
    start_time = time()
    last_sec = int(start_time)
    while True:
      t = int(time())
      if t != last_sec:
        if not self.Timers[user]['first_run']:
          sys.stdout.write("\b"*5)
        if self.Timers[user]['first_run']:
          self.Timers[user]['first_run'] = False
        sys.stdout.write(self.time_format(t, user, start_time))
        sys.stdout.flush()
        last_sec = t
        r, w, x = select.select([ sys.stdin ], [], [], 1)
        if r:
          btn = r[0].readline().strip()
          if btn == '':
            self.Timers[user]['timer'] = int(t - start_time) + 1
            self.Timers[user]['first_run'] = True
            break

  def move_piece(self):
    user = self.CurrentPlayer
    move = raw_input(user.upper() + ' >> ')
    if move.lower() == 'quit':
      if user == 'white':
        display_username = self.user_white
      else:
        display_username = self.user_black
      print "%s quits" % display_username
      x()
    piece, new_position = re.sub('\s+', '', move).split('->')
    piece = piece.upper()
    new_position = new_position.upper()
    piece_notation = piece
    new_position_notation = new_position
    square = self.board.Squares[new_position]
    ''' check if piece can make this move to start with '''
    piece_square = self.board.Squares[piece]
    if not piece_square.is_occupied():
      return (False, 'NO PIECE IN SQUARE',)
    piece = piece_square.get_piece()
    ''' check if piece belongs to the user '''
    if not piece.Color == user:      
      return (False, 'PIECE BELONGS TO THE OTHER USER',)
    ''' calculate row & column distance to new position '''
    column_diff = abs(Square.column_index(piece_notation[0]) - Square.column_index(new_position_notation[0]))
    row_diff = abs(Square.row_index(piece_notation[1]) - Square.row_index(new_position_notation[1]))
    ''' check if the move is in straight line '''
    straight_line = ( bool(piece_notation[0] != new_position_notation[0]) + bool(piece_notation[1] != new_position_notation[1]) ) == 1
    diagonal_line = False
    if not straight_line:
      if column_diff == row_diff:
        diagonal_line = True
    ''' check for L-shaped move (or gamma from the Greek letter Γ) '''
    gamma_move = False
    if column_diff == 2 or row_diff == 2:
      if column_diff == 2:
        if row_diff == 1:
          gamma_move = True
      if row_diff == 2:
        if column_diff == 1:
          gamma_move = True
    if gamma_move and not piece.DirectionGamma:
      return (False, 'L-SHAPED MOVES NOT PERMITTED FOR THIS PIECE',)
    
    if not diagonal_line and not straight_line and not gamma_move:
      return ( False, 'ILLEGAL MOVE',)
    ''' build the path consisting of the squares required for the move '''
    if not piece.LeapOverPiece:
      move_path = []
      min_row = min(Square.row_index(piece_notation[1]), Square.row_index(new_position_notation[1]))
      max_row = max(Square.row_index(piece_notation[1]), Square.row_index(new_position_notation[1]))
      min_col = min(Square.column_index(piece_notation[0]), Square.column_index(new_position_notation[0]))
      max_col = max(Square.column_index(piece_notation[0]), Square.column_index(new_position_notation[0]))
      ''' if movement happens in a straight line decide if move is vertical or horizontal '''
      if straight_line:
        if column_diff == 0:
          ''' vertical move '''
          column = Square.column_index(piece_notation[0])
          for r in range(min_row + 1, max_row):
            move_path.append(Square.position(r, column))
        else:
          ''' horizontal move '''      
          row = Square.column_index(piece_notation[1])
          for c in range(min_col + 1, max_col):
            move_path.append(Square.position(row, c))
      ''' 
      For diagonal movement we need to loop both rows and columns.
      Piece will have to cross squares where row offset equals 
      column offset from starting position.
      '''
      if diagonal_line:
        for c in range(min_col + 1, max_col):
          for r in range(min_row + 1, max_row):
            if (r - min_row) == (c - min_col):
              move_path.append(Square.position(r, c))
    ''' Check move length and reject if exceeds permitted number '''
    if piece.MaxSquares > 0 and (len(move_path) + 1) > piece.MaxSquares:
      return (False, 'PIECE HAS LIMITED SQUARE NUMBER PER MOVE',)
    ''' Check if any squares in the move path are occupied '''
    for path_square in move_path:
      if self.board.Squares[path_square].is_occupied():
        return ( False, 'MOVE PATH IS BLOCKED', )
    ''' Check if the square is occupied from the same player's pieces '''
    if square.is_occupied():
      if square.get_piece().Color == user:
        return ( False, 'TARGET SQUARE ALREADY OCCUPIED WITH USER PIECE', )
    ''' Remove the piece from its current position '''
    self.board.Squares[piece_notation].set_piece(None)
    ''' Place the piece in the target square '''
    self.board.Squares[new_position_notation].set_piece(piece)
    ''' Change the player '''
    self.change_player()
    return ( True, '', )

  def change_player(self):
    ''' Perform any actions necessary to change the current player '''
    if self.CurrentPlayer == 'white':
      self.CurrentPlayer = 'black'
    else:
      self.CurrentPlayer = 'white'

  def __str__(self):
    ''' Fetch the board representation at the current state. '''
    b = str(self.board) # Get the board string representation
    l = len(b.split("\n")[0]) # find the length of the first line
    ''' 
    Use format to display the usernames centered on top and bottom respectively 
    (depending which color each player is assigned) 
    '''
    user = "{user:^%d}\n" % l     
    ''' Add usernames to the board '''
    board = user.format(user=self.user_black)
    board += b + '\n'
    board += user.format(user=self.user_white)
    return board    

if __name__ == '__main__':
  ''' 
  Parse command line arguments;
  -h/--help is reserved by default and will display all available parameters.
  '''
  argparser = argparse.ArgumentParser('Python Console Chessboard')
  argparser.add_argument('--user1', help = '1st username', default = 'User #1')
  argparser.add_argument('--user2', help = '2nd username', default = 'User #2')
  arguments = argparser.parse_args() 

  ''' Start the game '''
  game = Game(arguments)
  game.board.setup()
  ''' Display initial board setup '''
  print game
  while True:
    ''' Start the timer for the current player '''
    game.start_timer()
    ''' Request a piece move '''
    move_legal, message = game.move_piece()
    if move_legal:
      ''' If move is legal, show changed board '''
      print game  
    else:
      ''' Otherwise request a new move from the player '''
      print '%s, PLEASE PLAY AGAIN' % (message,)
  

