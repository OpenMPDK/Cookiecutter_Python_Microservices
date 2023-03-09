from cliff.interactive import InteractiveApp


# noinspection PyRedeclaration
class InteractiveApp(InteractiveApp):
    """
    placeholder class for customizing the Interactive App
    """
    # def default(self, line):
    #     if hasattr(self, 'LOG'):
    #         _log = self.LOG
    #     else:
    #         _log = getLogger(__name__)
    #     print(line)
    #     _log.info(line)
    #     print(line.parsed)
    #     _log.info(line.parsed)
    #     print(line.parsed.raw)
    #     _log.info(line.parsed.raw)
    #     line_parts = shlex.split(line.parsed.raw)
    #     print(line_parts)
    #     _log.info(line)

    # try: self.parent_app.run_subcommand(line_parts) except EmbeddedConsoleExit as e: return 1 #This is breaking the
    # environment as default command processor is considered as cmd2.default, instead of cliff.InteractiveApp.default
    # Looks this change is from python 3.x support
    pass
