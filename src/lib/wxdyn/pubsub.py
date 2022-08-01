import asyncio
import functools
import time
import lib.wxdyn.log as  log


class Subscriber:
    def update(self, message):
        print('{} got message "{}"'.format(self.name, message))

class Publisher:
    def __init__(self, events):
        # self.events is a dictionary that maps event names to subscriptions to that event
        # each subscription is a dictionary that maps subscribers (objects) to event handlers (functions)
        # for instance: self.events = {"msg_new_project": {<subscriber1>: <function1>, <subscriber2>: <function2>}}
        self.events = { event : dict() for event in events }

    def __destroy__(self):
        del self.mq
        del self.events
    
    def get_subscribers(self, event):
        return self.events[event]

    def subscribe(self, subscriber, event, handler):
        if handler == None: return
        if not subscriber in self.get_subscribers(event):
            self.get_subscribers(event)[subscriber] = handler

    def unsubscribe(self, event, subscriber):
        if event in self.events and subscriber in self.events[event]:
            del self.events[event][subscriber]

    def dispatch(self, event, payload):
        log.debug(function=self.dispatch, args=(event, payload))
        if payload:
            payload.update({"event": event})
        else:
            payload = {"event": event}

        messages = list()
        for subscriber, handler in self.get_subscribers(event).items():
            log.debug("append message: ", handler.__qualname__, function=self.dispatch)
            messages.append((handler, payload))

        if len(messages)>0:
            MessageQueue.processMessages(messages)

class MessageQueue:
    MAXQUEUESIZE = 20
    instance = None
    asyncOff = False
    
    # This inner class represent a singleton (it should only have a single instance)
    class __MessageQueue__:
        def __init__(self, maxQueueSize):
            self.sent = 0
            self.cumql = 0
            self.maxql = 0
            self.cumpt = 0.0
            self.maxpt = 0.0
            self.queue = []
            
        def reset(self):
            self.queue = []

        def getStats(self):
            return (self.sent, self.maxql, 0 if self.sent==0 else int(self.cumql/self.sent), self.maxpt, 0 if self.sent==0 else self.cumpt/self.sent)

        def getStatsStr(self):
            s = "MQ Stats: sent:{}, max queue len: {}, av queue len: {}, max proc time: {:0.2f} s, av proc time: {:0.2f} s"
            return s.format(*self.getStats())
            
        def push(self, messages):
            if messages:
                self.queue.extend(messages)
                ql = len(self.queue)
                if ql>self.maxql: self.maxql = ql 
                if self.sent % 20 == 0: 
                    log.trace(self.getStatsStr())

        def hasMessages(self):
            return (len(self.queue)>0)
        
        def handleNextMessage(self):
            if self.hasMessages():
                ql = len(self.queue)
                msg = self.queue.pop(0)
                if msg:
                    handler = msg[0]
                    payload = msg[1]
                    log.debug("handle msg: ", payload["event"], handler.__qualname__, function=self.handleNextMessage)
                    try:
                        tic = time.perf_counter()
                        handler(payload)
                        toc = time.perf_counter()
                        self.sent+=1
                        self.cumql+=ql
                        if toc-tic>self.maxpt: self.maxpt = toc-tic
                        self.cumpt+=(toc-tic)
                    except RuntimeError as re:
                        log.error(re, function = self.handleNextMessage)
                        raise re
                    except AttributeError as ae:
                        log.error(ae, function = self.handleNextMessage)
 
    # class method for obtaining the singleton instance of __MessageQueue__
    def getInstance(asyncOff=False):
        if MessageQueue.instance == None: 
            MessageQueue.instance = MessageQueue.__MessageQueue__(MessageQueue.MAXQUEUESIZE)
            MessageQueue.asyncOff = asyncOff
        return MessageQueue.instance
    
    def getStats(asyncOff=False):
        mq = MessageQueue.getInstance(asyncOff)
        if mq:
            return mq.getStats()

    def reset(asyncOff=False):
        mq = MessageQueue.getInstance(asyncOff)
        if mq:
            mq.reset()

    def handleMessages():
        mq = MessageQueue.getInstance()
        while mq:
            mq.handleNextMessage()
            if not mq.hasMessages(): break

    def addMessages(messages):
        mq = MessageQueue.getInstance()
        if mq:
            mq.push(messages)
                
    def processMessages(messages):
        if MessageQueue.asyncOff:
            MessageQueue.addMessages(messages)
            MessageQueue.handleMessages()
        else:
            loop = asyncio.get_running_loop()

            try:
                callback = functools.partial(MessageQueue.addMessages, messages)
                loop.call_soon_threadsafe(callback)
            finally:
                pass

            try:
                callback = MessageQueue.handleMessages
                loop.call_soon_threadsafe(callback)
            finally:
                pass
            
