"""Registry containing my custom tools."""

from portia import InMemoryToolRegistry
#from my_custom_tools.file_reader_tool import FileReaderTool
#from my_custom_tools.file_writer_tool import FileWriterTool
from my_web3_tools.fetch_wallet_balance_tool import CheckWalletBalanceTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        CheckWalletBalanceTool(),
        #FileReaderTool(),
        #FileWriterTool(),
    ],
)