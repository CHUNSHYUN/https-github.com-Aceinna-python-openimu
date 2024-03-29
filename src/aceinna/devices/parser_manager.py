from .parsers.open_message_parser import UartMessageParser as OpenUartMessageParser
from .parsers.dmu_message_parser import UartMessageParser as DMUUartMessageParser
from .parsers.ins2000_message_parser import UartMessageParser as INS2000UartMessageParser
from .parsers.ins401_message_parser import EthernetMessageParser as INS401EthernetMessageParser

class ParserManager:
    '''
    Manage Parser
    '''
    device_list = []

    # TODO: communicator_type should be used to generate the parser
    @staticmethod
    def build(device_type, communicator_type, properties):  # pylint:disable=unused-argument
        '''
        Generate matched parser
        '''
        if device_type == 'DMU':
            return DMUUartMessageParser(properties)
        elif device_type == 'INS2000':
            return INS2000UartMessageParser(properties)
        elif device_type == 'INS401':
            return INS401EthernetMessageParser(properties)
        else:
            return OpenUartMessageParser(properties)
