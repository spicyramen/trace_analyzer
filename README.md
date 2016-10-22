# Freeswitch log parser

Instructions:

Enable Freeswitch SIP traces.

'''
#fs_cli

>fsctl loglevel 3
>sofia tracelevel 3
>sofia profile external siptrace on

'''

Running:

Collect freeswitch logs:
For simple log file, just extract latest freeswitch.log
Otherwise extract freeswitch.log.* and concatenate all the files.
Latest file is freeswitch.log

cat freeswitch.log.* > freeswitch.log.all

Run script

'''
#python sip_parser.py <freeswitch.log filename>

Example:
#python sip_parser.py freeswitch.log.all

'''

Functions:

readFile(): Reads file and returns SIP Messages
printSipMessages(sipMessage arr*): Prints all SIP messages, including SDP.
sipCalls(): Reads SIP messages array and return SIP Call dictionary using SIP call_id as key and value SIP messages array.
analyzeSipCalls(): Performs processing/parsing. Like extracting SIP logs.


I have tested file with 100K calls ~600MB.


