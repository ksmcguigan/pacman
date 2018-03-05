# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import distanceCalculator
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.timer = 0.0
    self.foodCollected = 0
    '''
    Your initialization code goes here, if you need any.
    '''

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    if self.timer > 0:
    	self.timer -= 1

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values) #this gets the best action VV
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    choice = random.choice(bestActions)
    if self.getSuccessor(gameState, choice).getAgentPosition(self.index) in self.getFood(gameState).asList():
      #you bout to eat a food
      self.foodCollected += 1

    if self.foodCollected >= 6:
      #print "heading home"
      choice = self.headHome(gameState)
    return choice

  def headHome(self, gameState):
    # head on home and avoid ghosts
    dist = float('inf')
    bestAction = Directions.STOP

    for a in gameState.getLegalActions(self.index):
      succ = self.getSuccessor(gameState, a)
      if self.getClosestEnemyPosition(succ) < 5:
        continue

      myNextPos = succ.getAgentState(self.index).getPosition()
      if self.getMazeDistance(myNextPos,self.start) < dist:
        dist = self.getMazeDistance(myNextPos,self.start)
        bestAction = a
        #print bestAction

    if self.getSuccessor(gameState, bestAction).getAgentState(self.index).isPacman:
      x = 1
    else:
      self.foodCollected = 0

    return bestAction

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    #print features
    #print weights
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def getEnemies(self, gameState):
    ## returns a list of the enemy agents and their positions
    enemies = list()
  #  enemies = [(gameState.getAgentState(i), gameState.getAgentPosition(i)) for i in self.getOpponents(gameState)]
    #get agent position returns 'None' because they are not observable!
    for i in self.getOpponents(gameState):
      if gameState.getAgentPosition(i) == None:
        #not close enough! must estimate location

        x = 1
      else:
        enemies.append((gameState.getAgentState(i), gameState.getAgentPosition(i)))
    #print enemies
    return enemies #Currently, this only gets the visible enemies

  def estimateClosestEnemyDistance(self, gameState):
    #estimate distance to closest enemy
    return 1

  def distanceToCenterOfTerritory(self, gameState):
    x = gameState.getWalls().width / 2 

    if self.red:
      x = x - 1 #normally minus 1

    yvals = [y for y in xrange(gameState.getWalls().height)]
    y = random.choice(yvals)

    while gameState.hasWall(x, y):
      y = random.choice(yvals)

    center = (x, y)

    myPos = gameState.getAgentState(self.index).getPosition()
    dist = self.getMazeDistance(myPos, center)

    return dist


  def getClosestEnemyPosition(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    closest = float('inf')
    for enemy, pos in self.getEnemies(gameState):
      if self.getMazeDistance(myPos, pos) < closest:
        closest = self.getMazeDistance(myPos, pos)
      if self.getMazeDistance(myPos, pos) == 0:
        return 1000
    return closest

  def getInvaders(self, gameState):
    invaders = list()
    invaders = [(e, p) for e, p in self.getEnemies(gameState) if e.isPacman]# and e.getPosition() != None]
    return invaders

class OffensiveReflexAgent(DummyAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 100 - minDistance

    # Distance to closest visible enemy

    c = self.getClosestEnemyPosition(successor)
    #print c
    if c == float('inf'):
      features['closestEnemy'] = 0
    else:
      features['closestEnemy'] = c #avoid getting eaten!
      features['distanceToFood'] = 0
      features['closestCapsule'] = 0
      features['successorScore'] = 0
      return features

    # Get distance to closest big food ball using getCapsules(gameState)
    closestCapsule = 0
    if len(self.getCapsules(successor)):
      closestCapsule = min([self.getMazeDistance(myPos, cap) for cap in self.getCapsules(successor)])
      #print closestCapsule
      if closestCapsule != 0:
        features['closestCapsule'] = 1 / closestCapsule

    # If ate one, 40 ignore closest enemy and emphasize eating food. TAKE THIS ACTION
    if myPos in self.getCapsules(successor):
      self.timer = 40
    if self.timer > 0:
      features['distanceToFood'] *= 10000
      features['closestEnemy'] = 0
      features['closestCapsule'] = 0

    # Get distance to other allies to avoid grouping

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': 1, 'closestEnemy': -50, 'closestCapsule': 1}

class DefensiveReflexAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    invaders = self.getInvaders(successor)
    features['numInvaders'] = len(invaders)
    features['center'] = 0
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, p) for a, p in invaders]
      features['invaderDistance'] = min(dists)
    else:
      #no visible invaders, just head towards center of territory for now
      features['center'] = self.distanceToCenterOfTerritory(successor)
    #else:
    #  foodToProtect = self.getFoodYouAreDefending(successor).asList()
    #  if len(foodToProtect) > 0:
    #    minDistance = min([self.getMazeDistance(myPos, food) for food in foodToProtect])
    #    features['protect'] = minDistance

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    #avoid allies close to you

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -100, 'stop': -100, 'reverse': -2, 'center': -10}
