"""This module defines a detector for new data paths."""

import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import PersistencyUtil
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class NewMatchPathDetector(AtomHandlerInterface, \
    TimeTriggeredComponentInterface, EventSourceInterface):
  """This class creates events when new data path was found in
  a parsed atom."""

  def __init__(self, aminerConfig, anomalyEventHandlers, \
    persistenceId='Default', autoIncludeFlag=False, outputLogLine=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location."""
    self.anomalyEventHandlers = anomalyEventHandlers
    self.autoIncludeFlag = autoIncludeFlag
    self.nextPersistTime = None
    self.outputLogLine = outputLogLine
    self.aminerConfig = aminerConfig

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        aminerConfig, self.__class__.__name__, persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is None:
      self.knownPathSet = set()
    else:
      self.knownPathSet = set(persistenceData)


  def receiveAtom(self, logAtom):
    """Receive on parsed atom and the information about the parser
    match.
    @param logAtom the parsed log atom
    @return True if this handler was really able to handle and
    process the match. Depending on this information, the caller
    may decide if it makes sense passing the parsed atom also
    to other handlers."""
    unknownPathList = []
    for path in logAtom.parserMatch.getMatchDictionary().keys():
      if path not in self.knownPathSet:
        unknownPathList.append(path)
        if self.autoIncludeFlag:
          self.knownPathSet.add(path)
    if unknownPathList:
      if self.nextPersistTime is None:
        self.nextPersistTime = time.time()+600
      if self.outputLogLine:
        originalLogLinePrefix = self.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
        if originalLogLinePrefix is None:
          originalLogLinePrefix = ''
        sortedLogLines = [logAtom.parserMatch.matchElement.annotateMatch(''), 
          originalLogLinePrefix+repr(logAtom.rawData)]
      else:
        sortedLogLines = [logAtom.parserMatch.matchElement.annotateMatch('')]
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__, 'New path(es) detected', 
            sortedLogLines, logAtom, self)
    return True


  def getTimeTriggerClass(self):
    """Get the trigger class this component can be registered
    for. This detector only needs persisteny triggers in real
    time."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def doTimer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime is None:
      return 600

    delta = self.nextPersistTime-triggerTime
    if delta <= 0:
      self.doPersist()
      delta = 600
    return delta

  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime = None

  def whitelistEvent(self, eventType, sortedLogLines, eventData, \
      whitelistingData):
    """Whitelist an event generated by this source using the information
    emitted when generating the event.
    @return a message with information about whitelisting
    @throws Exception when whitelisting of this special event
    using given whitelistingData was not possible."""
    if eventType != 'Analysis.%s' % self.__class__.__name__:
      raise Exception('Event not from this source')
    if whitelistingData is not None:
      raise Exception('Whitelisting data not understood by this detector')
    whitelistedStr = ''
    for pathName in eventData[1]:
      if pathName in self.knownPathSet:
        continue
      self.knownPathSet.add(pathName)
      if whitelistedStr:
        whitelistedStr += ', '
      whitelistedStr += repr(pathName)
    return 'Whitelisted path(es) %s in %s' % (whitelistedStr, sortedLogLines[0])
