import re
import sys


class sipMessage():
    """Create a SIP Message Object"""

    def __init__(self):
        self._sipMsgMethodInfo = None
        self._sipHeaderInfo = list()
        self._sipMsgSdpInfo = list()
        self._sipUuid = None
        self._sipCampaign = None
        self._sipCallId = None
        self._sipUri = None
        self.hasSDP = False
        self.sipMsgCallId = ''

    @property
    def sipUri(self):
        return self._sipUri

    @sipUri.setter
    def sipUri(self, uri):
        self._sipUri = uri

    @property
    def sipUuid(self):
        return self._sipUuid

    @sipUuid.setter
    def sipUuid(self, uuid):
        self._sipUuid = uuid

    @property
    def sipCallId(self):
        return self._sipCallId

    @sipCallId.setter
    def sipCallId(self, callId):
        self._sipCallId = callId

    @property
    def sipCampaign(self):
        return self._sipCampaign

    @sipCampaign.setter
    def sipCampaign(self, campaign):
        self.sipCampaign = campaign

    @property
    def sipMsgMethodInfo(self):
        """

        :return:
        """
        return self._sipMsgMethodInfo

    @sipMsgMethodInfo.setter
    def sipMsgMethodInfo(self, msg):
        """

        :param msg:
        :return:
        """
        self._sipMsgMethodInfo = msg

    @property
    def sipHeaderInfo(self):
        return self._sipHeaderInfo

    def setUri(self, header):
        """

        :param header:
        :return:
        """
        sip_uri = re.search(r'\<sip:(\+?\w+)@.*', header)
        if sip_uri:
            self.sipUri = sip_uri.group(1)

    @sipHeaderInfo.setter
    def sipHeaderInfo(self, headerInfo):
        """

        :param headerInfo:
        :return:
        """
        self._sipHeaderInfo = headerInfo

    def addSipHeader(self, header, value):
        """

        :param header:
        :param value:
        :return:
        """
        if "Call-ID:" in header:
            self.sipCallId = value

        self.sipHeaderInfo.append((header, value))

    def addSdpInfo(self, sdpLineNumber, sdpKey, sdpValue):
        """

        :param sdpLineNumber:
        :param sdpKey:
        :param sdpValue:
        :return:
        """
        self.hasSDP = True
        sdpLine = sdpKey + '=' + sdpValue
        self._sipMsgSdpInfo.append(sdpLine)

    def processSipHeaders(self):
        """

        :return:
        """
        for header in self.sipHeaderInfo:
            print header[0], header[1]

    def processSipMsgSdp(self):
        """

        :return:
        """
        if self.hasSDP:
            print ""
            for sdpLine in self._sipMsgSdpInfo:
                print sdpLine


def readFile(filename):
    """

    :param filename:
    :return:
    """
    sipMessages = list()
    with open(filename) as f:
        for line in f:
            sipLine = line.rstrip('\n')
            sipLine = sipLine.strip()
            sdpLine = 1
            Message = re.search(r'(\w+\s+sip:.*)|(^SIP/2.0\s.*)', sipLine)
            Header = re.search(r'(^\w+:) (.*)|([A-Za-z]+-[A-Za-z]+:) (.*)', sipLine)
            SDP = re.search(r'(^[A-Za-z]){1}=(.*)', sipLine)
            if sipLine == '------------------------------------------------------------------------':
                sipMessageObject = None

            if Message:
                sipMessageObject = sipMessage()
                sipMessages.append(sipMessageObject)
                message = Message.group(0)
                sipMessageObject.sipMsgMethodInfo = message
                Message = None

            if Header:
                headerKey = Header.group(1)
                headerValue = Header.group(2)
                if ((headerKey is None) and (headerValue is None)):
                    headerKey = Header.group(3)
                    headerValue = Header.group(4)
                sipMessageObject.addSipHeader(headerKey, headerValue)
                if "INVITE" in message:
                    if "To:" in headerKey:
                        sipMessageObject.setUri(headerValue)
                    if "X-UUID:" in headerKey:
                        sipMessageObject.sipUuid = headerValue
                    if "X-Campaign:" in headerKey:
                        sipMessageObject.sipCampaign = headerValue
                Header = None

            if SDP:
                sdpKey = SDP.group(1)
                sdpValue = SDP.group(2)
                sipMessageObject.addSdpInfo(sdpLine, sdpKey, sdpValue)
                sdpLine = + 1
                SDP = None

    return sipMessages


def sipCalls(sipMessages):
    """
    For each sipMessage extract sip Call-ID and use it as key in a Dictionary
        Value is an Array containing each SipMessage for the call in order SIP Message was received/parsed.
    :param sipMessages:
    :return:
    """
    sipCalls = dict()
    for sipMsg in sipMessages:
        if sipMsg:
            if sipMsg.sipCallId in sipCalls:
                sipCalls[sipMsg.sipCallId].append(sipMsg)
            else:
                sipCalls[sipMsg.sipCallId] = list()
                sipCalls[sipMsg.sipCallId].append(sipMsg)

    return sipCalls


def getSipCallUuid(sipMessages):
    """

    :param sipMessages:
    :return:
    """
    for sipMsg in sipMessages:
        if sipMsg:
            if sipMsg.sipUuid:
                return sipMsg.sipUuid,


def printSipCalls(sipCalls, callid=None):
    """
    Print all Sip Messages for all Calls
    :param sipCalls:
    :param callid:
    :return:
    """
    for k, v in sipCalls.iteritems():
        if callid is None:
            # print k
            error = printSipMessages(v, True)
            if error:
                print error
        else:
            if callid == k:
                printSipMessages(v, True)


def analyzeSipCalls(sipCalls, callid=None):
    """
    Print all Sip Messages for all Calls
    :param sipCalls:
    :param callid:
    :return:
    """
    for k, v in sipCalls.iteritems():
        if callid is None:
            normalize = callAnalyzer(v)
            if normalize:
                print k
        else:
            if callid == k:
                printSipMessages(v, True)


def callAnalyzer(sipMessages):
    """
    Handle Sip Call SIP Messages, analyzes SIP Messages that match certain condition.
    :param sipMessages:
    :return:
    """
    ringing = False
    temporaryUnavailable = False

    for sipMsg in sipMessages:
        if sipMsg:
            if "Ringing" in sipMsg.sipMsgMethodInfo:
                ringing = True
            if "480 Temporarily Unavailable" in sipMsg.sipMsgMethodInfo or \
                            "480 Temporarily not available" in sipMsg.sipMsgMethodInfo:
                temporaryUnavailable = True

    return ringing & temporaryUnavailable


def printSipMessages(sipMessages, process=False):
    """

    :param sipMessages:
    :return:
    """
    uuid = None
    for sipMsg in sipMessages:

        if sipMsg:
            # print "---------------------"
            print sipMsg.sipMsgMethodInfo
            # sipMsg.processSipHeaders()
            # sipMsg.processSipMsgSdp()
            if sipMsg.sipUuid:
                uuid = sipMsg.sipUuid
            if sipMsg.sipUri:
                uri = sipMsg.sipUri[3:]

            if process:
                values = getTwilioError(sipMsg)
                if values:
                    print uri + '|' + uuid + '|' + str('|'.join(values))
                    uri = None
                    uuid = None


def getTwilioError(sipMessage, errorType='01'):
    """

    :param sipMessage:
    :param errorType:
    :return:
    """
    callSid = None
    Reason = None
    callId = None
    twilioError = None

    if sipMessage:
        if errorType == '01':
            if "BYE" in sipMessage.sipMsgMethodInfo:
                sipHeaders = sipMessage.sipHeaderInfo
                for sipHeader in sipHeaders:
                    if 'Twilio-CallSid:' in sipHeader:
                        callSid = sipHeader[1]
                    if 'Reason:' in sipHeader:
                        Reason = sipHeader[1]
                    if 'Call-ID:' in sipHeader:
                        callId = sipHeader[1]
            if Reason and (callSid or callId):
                if "MVTSLocal" in Reason:
                    print callSid, "|", callId, "|", Reason
                    return callSid, callId, Reason

        if errorType == '02':
            if "Trunk CPS limit exceeded" in sipMessage.sipMsgMethodInfo:
                sipHeaders = sipMessage.sipHeaderInfo
                for sipHeader in sipHeaders:
                    if 'Twilio-Error:' in sipHeader:
                        twilioError = sipHeader[1]
                    if 'Call-ID:' in sipHeader:
                        callId = sipHeader[1]

            if twilioError and callId:
                return twilioError, callId


if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = '/Users/gogasca/Downloads/MX/9KBRPQ9IK3/9KBRPQ9IK3.all'

    if filename:
        allSipMessages = readFile(filename)
        printSipMessages(allSipMessages)
        allSipCalls = sipCalls(allSipMessages)
        analyzeSipCalls(allSipCalls, None)
